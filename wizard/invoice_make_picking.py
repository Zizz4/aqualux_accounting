from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, AccessDenied


class InvoiceMakePicking(models.TransientModel):
    _name = 'invoice.make.picking'
    _description = 'Create Picking From Invoice Wizard'

    user_id = fields.Many2one('res.users', string="Current User", default=lambda self: self.env.user)
    location_id = fields.Many2one('stock.location', string='Source Location', domain="[('warehouse_id.allowed_user_ids', 'in', user_id)]")
    dest_location_id = fields.Many2one('stock.location', string='Dest. Location', domain="[('warehouse_id.allowed_user_ids', 'in', user_id)]")
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')
    move_id = fields.Many2one('account.move', string='Invoice')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    move_type = fields.Selection([
        ('out_invoice', 'Cust. Invoice'),
        ('in_invoice', 'Vendor Bill')
    ])

    @api.model
    def default_get(self, fields):
        res = super(InvoiceMakePicking, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')

        move = self.env[active_model].browse(active_id)
        res.update({
            'move_id': move.id,
            'picking_type_id': move.picking_type_id.id,
            'picking_id': move.picking_id.id,
            'move_type': move.move_type,
        })

        return res

    @api.constrains('location_id')
    def _check_allowed_user(self):
        for record in self:
            # Skip if no location is selected
            if record.location_id:
                current_user = self.env.user
                # Check if the current user is in the allowed_user_ids of the selected location
                if current_user not in record.location_id.warehouse_id.allowed_user_ids:
                    raise UserError(_(
                        f"You are not allowed to select the location: {record.location_id.name}. "
                        "Please choose a location where you are listed as an allowed user."
                    ))

    @api.onchange('location_id', 'dest_location_id')
    def _onchange_operation_type_by_location(self):
        for rec in self:
            if rec.location_id:
                warehouse = rec.location_id.warehouse_id
                if warehouse:
                    if rec.move_type:
                        if rec.move_type == 'out_invoice':  # Outgoing (Delivery Order)
                            rec.picking_type_id = warehouse.out_type_id
                        elif rec.move_type == 'in_invoice':  # Incoming (Receipt)
                            rec.picking_type_id = warehouse.in_type_id
                        else:
                            rec.picking_type_id = False
                    else:
                        rec.picking_type_id = False
                else:
                    rec.picking_type_id = False
            if rec.dest_location_id:
                warehouse = rec.dest_location_id.warehouse_id
                if warehouse:
                    if rec.move_type:
                        if rec.move_type == 'out_invoice':  # Outgoing (Delivery Order)
                            rec.picking_type_id = warehouse.out_type_id
                        elif rec.move_type == 'in_invoice':  # Incoming (Receipt)
                            rec.picking_type_id = warehouse.in_type_id
                        else:
                            rec.picking_type_id = False
                    else:
                        rec.picking_type_id = False
                else:
                    rec.picking_type_id = False


    def create_picking_from_invoice(self):
        if not self.picking_type_id:
            raise UserError(_(" Please select a picking type"))
        for order in self:
            if not order.picking_id:
                pick = {}
                if order.picking_type_id.code == 'outgoing':
                    pick = {
                        'picking_type_id': order.picking_type_id.id,
                        'partner_id': order.move_id.partner_id.id,
                        'origin': order.move_id.name,
                        'location_dest_id': order.move_id.partner_id.property_stock_customer.id,
                        'location_id': order.location_id.id,
                        'move_type': 'direct'
                    }
                if order.picking_type_id.code == 'incoming':
                    pick = {
                        'picking_type_id': order.picking_type_id.id,
                        'partner_id': order.move_id.partner_id.id,
                        'origin': order.move_id.name,
                        'location_dest_id': order.dest_location_id.id,
                        'location_id': order.move_id.partner_id.property_stock_supplier.id,
                        'move_type': 'direct'
                    }
                picking = self.env['stock.picking'].create(pick)
                order.move_id.picking_id = picking.id
                order.move_id.transfer_ids = [(4, picking.id)]
                moves = order.move_id.invoice_line_ids.filtered(
                    lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)
                move_ids = moves._action_confirm()
                move_ids._action_assign()

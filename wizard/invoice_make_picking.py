from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, AccessDenied


class InvoiceMakePicking(models.TransientModel):
    _name = 'invoice.make.picking'
    _description = 'Create Picking From Invoice Wizard'

    location_id = fields.Many2one('stock.location', string='Warehouse')
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')
    move_id = fields.Many2one('account.move', string='Invoice')
    picking_id = fields.Many2one('stock.picking', string='Picking')
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
        })

        return res

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
                        'location_dest_id': order.location_id,
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
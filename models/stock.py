from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_count = fields.Integer(string='Invoices',
                                   compute='_compute_invoice_count')
    operation_code = fields.Selection(related='picking_type_id.code', string="Operation Type Code",
                                      help="For technical purposes only")
    is_return = fields.Boolean()

    def _compute_invoice_count(self):
        """This compute function used to count the number of invoice for
        the picking"""
        for picking_id in self:
            move_ids = picking_id.env['account.move'].search(
                [('transfer_ids', 'in', picking_id.id)])
            if move_ids:
                self.invoice_count = len(move_ids)
            else:
                self.invoice_count = 0

    def create_invoice(self):
        """This is the function for creating customer invoice
        from the picking"""
        for picking_id in self:
            current_user = self.env.uid
            if picking_id.picking_type_id.code == 'outgoing':
                customer_journal_id = \
                    picking_id.env['ir.config_parameter'].sudo(). \
                        get_param('stock_move_invoice.customer_journal_id') or \
                    False
                if not customer_journal_id:
                    raise UserError(
                        _("Please configure the journal from settings"))
                invoice_line_list = []
                for move_ids_without_package in picking_id. \
                        move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit':
                            move_ids_without_package.product_id.lst_price,
                        'account_id':
                            move_ids_without_package.product_id.
                            property_account_income_id.id if
                            move_ids_without_package.
                            product_id.property_account_income_id
                            else move_ids_without_package.
                            product_id.categ_id.
                            property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [
                            picking_id.company_id.account_sale_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    invoice_line_list.append(vals)
                    invoice = picking_id.env['account.move'].create({
                        'move_type': 'out_invoice',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': current_user,
                        'narration': picking_id.name,
                        'partner_id': picking_id.partner_id.id,
                        'currency_id':
                            picking_id.env.user.company_id.currency_id.id,
                        'journal_id': int(customer_journal_id),
                        'payment_reference': picking_id.name,
                        'picking_id': picking_id.id,
                        'invoice_line_ids': invoice_line_list,
                        'transfer_ids': self
                    })
                    return invoice

    def create_bill(self):
        """This is the function for creating vendor bill
                from the picking"""
        for picking_id in self:
            current_user = self.env.uid
            if picking_id.picking_type_id.code == 'incoming':
                vendor_journal_id = picking_id.env[
                                        'ir.config_parameter'].sudo().get_param(
                    'stock_move_invoice.vendor_journal_id') or False
                if not vendor_journal_id:
                    raise UserError(
                        _("Please configure the journal from the settings."))
                invoice_line_list = []
                for move_ids_without_package in picking_id. \
                        move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit':
                            move_ids_without_package.product_id.lst_price,
                        'account_id':
                            move_ids_without_package.product_id.
                            property_account_income_id.id if
                            move_ids_without_package.product_id.
                            property_account_income_id
                            else move_ids_without_package.product_id.categ_id.
                            property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [
                            picking_id.company_id.account_purchase_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    invoice_line_list.append(vals)
                    invoice = picking_id.env['account.move'].create({
                        'move_type': 'in_invoice',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': current_user,
                        'narration': picking_id.name,
                        'partner_id': picking_id.partner_id.id,
                        'currency_id':
                            picking_id.env.user.company_id.currency_id.id,
                        'journal_id': int(vendor_journal_id),
                        'payment_reference': picking_id.name,
                        'picking_id': picking_id.id,
                        'invoice_line_ids': invoice_line_list,
                        'transfer_ids': self
                    })
                    return invoice

    def create_customer_credit(self):
        """This is the function for creating customer credit note
                from the picking"""
        for picking_id in self:
            current_user = picking_id.env.uid
            if picking_id.picking_type_id.code == 'incoming':
                customer_journal_id = \
                    picking_id.env['ir.config_parameter'].sudo(). \
                        get_param('stock_move_invoice.customer_journal_id') or \
                    False
                if not customer_journal_id:
                    raise UserError(
                        _("Please configure the journal from settings"))
                invoice_line_list = []
                for move_ids_without_package in picking_id. \
                        move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit':
                            move_ids_without_package.product_id.lst_price,
                        'account_id': move_ids_without_package.product_id.
                            property_account_income_id.id if
                        move_ids_without_package.product_id.
                            property_account_income_id
                        else move_ids_without_package.product_id.categ_id.
                            property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [
                            picking_id.company_id.account_sale_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    invoice_line_list.append(vals)
                    invoice = picking_id.env['account.move'].create({
                        'move_type': 'out_refund',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': current_user,
                        'narration': picking_id.name,
                        'partner_id': picking_id.partner_id.id,
                        'currency_id':
                            picking_id.env.user.company_id.currency_id.id,
                        'journal_id': int(customer_journal_id),
                        'payment_reference': picking_id.name,
                        'picking_id': picking_id.id,
                        'invoice_line_ids': invoice_line_list,
                        'transfer_ids': self
                    })
                    return invoice

    def create_vendor_credit(self):
        """This is the function for creating refund
                from the picking"""
        for picking_id in self:
            current_user = self.env.uid
            if picking_id.picking_type_id.code == 'outgoing':
                vendor_journal_id = picking_id.env[
                                        'ir.config_parameter'].sudo().get_param(
                    'stock_move_invoice.vendor_journal_id') or False
                if not vendor_journal_id:
                    raise UserError(
                        _("Please configure the journal from the settings."))
                invoice_line_list = []
                for move_ids_without_package in picking_id. \
                        move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit':
                            move_ids_without_package.product_id.lst_price,
                        'account_id': move_ids_without_package.product_id.
                            property_account_income_id.id if
                        move_ids_without_package.product_id.
                            property_account_income_id
                        else move_ids_without_package.product_id.categ_id.
                            property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [
                            picking_id.company_id.account_purchase_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    invoice_line_list.append(vals)
                    invoice = picking_id.env['account.move'].create({
                        'move_type': 'in_refund',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': current_user,
                        'narration': picking_id.name,
                        'partner_id': picking_id.partner_id.id,
                        'currency_id':
                            picking_id.env.user.company_id.currency_id.id,
                        'journal_id': int(vendor_journal_id),
                        'payment_reference': picking_id.name,
                        'picking_id': picking_id.id,
                        'invoice_line_ids': invoice_line_list,
                        'transfer_ids': self
                    })
                    return invoice

    def action_open_picking_invoice(self):
        """This is the function of the smart button which redirect to the
        invoice related to the current picking"""
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('transfer_ids', 'in', self.id)],
            'context': {'create': False},
            'target': 'current'
        }

    def action_create_multi_invoice_for_multi_transfer(self):
        """This is the function for creating customer invoice
        from the picking"""
        picking_type = list(self.picking_type_id)
        if all(first == picking_type[0] for first in picking_type):
            if self.picking_type_id.code == 'outgoing':
                partner = list(self.partner_id)
                if all(first == partner[0] for first in partner):
                    partner_id = self.partner_id
                    invoice_line_list = []
                    customer_journal_id = \
                        self.env['ir.config_parameter'].sudo(). \
                            get_param('stock_move_invoice.customer_journal_id') \
                        or False
                    if not customer_journal_id:
                        raise UserError(
                            _("Please configure the journal from settings"))
                    for picking_id in self:
                        for move_ids_without_package in picking_id. \
                                move_ids_without_package:
                            vals = (0, 0, {
                                'name':
                                    move_ids_without_package.description_picking
                                ,
                                'product_id':
                                    move_ids_without_package.product_id.id,
                                'price_unit': move_ids_without_package.
                                    product_id.lst_price,
                                'account_id': move_ids_without_package.
                                    product_id.property_account_income_id.id if
                                move_ids_without_package.product_id.
                                    property_account_income_id
                                else move_ids_without_package.
                                    product_id.categ_id.
                                    property_account_income_categ_id.id,
                                'tax_ids': [(6, 0, [picking_id.company_id.
                                             account_purchase_tax_id.id])],
                                'quantity':
                                    move_ids_without_package.quantity_done,
                            })
                            invoice_line_list.append(vals)
                    invoice = self.env['account.move'].create({
                        'move_type': 'out_invoice',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': self.env.uid,
                        'narration': picking_id.name,
                        'partner_id': partner_id.id,
                        'currency_id':
                            picking_id.env.user.company_id.currency_id.id,
                        'journal_id': int(customer_journal_id),
                        'payment_reference': picking_id.name,
                        'invoice_line_ids': invoice_line_list,
                        'transfer_ids': self
                    })
                else:
                    for picking_id in self:
                        picking_id.create_invoice()
            elif self.picking_type_id.code == 'incoming':
                partner = list(self.partner_id)
                if all(first == partner[0] for first in partner):
                    partner_id = self.partner_id
                    bill_line_list = []
                    vendor_journal_id = \
                        self.env['ir.config_parameter'].sudo(). \
                            get_param('stock_move_invoice.vendor_journal_id') \
                        or False
                    if not vendor_journal_id:
                        raise UserError(_("Please configure the journal from "
                                          "the settings."))
                    for picking_id in self:
                        for move_ids_without_package in picking_id. \
                                move_ids_without_package:
                            vals = (0, 0, {
                                'name':
                                    move_ids_without_package.description_picking
                                ,
                                'product_id':
                                    move_ids_without_package.product_id.id,
                                'price_unit': move_ids_without_package.
                                    product_id.lst_price,
                                'account_id': move_ids_without_package.
                                    product_id.property_account_income_id.id if
                                move_ids_without_package.product_id.
                                    property_account_income_id
                                else move_ids_without_package.
                                    product_id.categ_id.
                                    property_account_income_categ_id.id,
                                'tax_ids': [(6, 0, [picking_id.company_id.
                                             account_purchase_tax_id.id])],
                                'quantity':
                                    move_ids_without_package.quantity_done,
                            })
                            bill_line_list.append(vals)
                    invoice = self.env['account.move'].create({
                        'move_type': 'in_invoice',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': self.env.uid,
                        'narration': picking_id.name,
                        'partner_id': partner_id.id,
                        'currency_id':
                            picking_id.env.user.company_id.currency_id.id,
                        'journal_id': int(vendor_journal_id),
                        'payment_reference': picking_id.name,
                        'picking_id': picking_id.id,
                        'invoice_line_ids': bill_line_list,
                        'transfer_ids': self
                    })
                else:
                    for picking_id in self:
                        picking_id.create_bill()
        else:
            raise UserError(
                _("Please select single type transfer"))


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    allowed_user_ids = fields.Many2many(comodel_name='res.users', string='Allowed User')


class StockReturnInvoicePicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        """in this function the picking is marked as return"""

        new_picking, pick_type_id = \
            super(StockReturnInvoicePicking, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'is_return': True})
        return new_picking, pick_type_id

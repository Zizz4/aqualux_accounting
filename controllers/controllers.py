# -*- coding: utf-8 -*-
# from odoo import http


# class AqualuxAccounting(http.Controller):
#     @http.route('/aqualux_accounting/aqualux_accounting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aqualux_accounting/aqualux_accounting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('aqualux_accounting.listing', {
#             'root': '/aqualux_accounting/aqualux_accounting',
#             'objects': http.request.env['aqualux_accounting.aqualux_accounting'].search([]),
#         })

#     @http.route('/aqualux_accounting/aqualux_accounting/objects/<model("aqualux_accounting.aqualux_accounting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aqualux_accounting.object', {
#             'object': obj
#         })

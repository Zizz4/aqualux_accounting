# -*- coding: utf-8 -*-
{
    'name': "Aqualux Accounting",

    'summary': """
        Module For Aqualux.
        """,

    'description': """
        Create Picking from Invoice.
        Create Invoice from Picking.
        Restrict User Warehouse.
    """,

    'author': "Erlan, Aziz",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '16.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/account_move.xml',
        'views/res_config_settings.xml',
        'views/stock_picking.xml',

        'wizard/picking_make_invoice.xml',
        'wizard/invoice_make_picking.xml',
    ]
}

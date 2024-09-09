# -*- coding: utf-8 -*-
{
    'name': "warranty_management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': -100,
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'mail', 'product','bi_all_in_one_helpdesk','bi_website_support_ticket','bi_subtask'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/warranty_rule.xml',
        'views/views.xml',
        'views/ir_sequence.xml',
        # 'views/warranty_claim.xml',
        # 'views/warranty_ticket.xml',
        'views/warranty_products.xml',
        'views/support_ticket.xml',

    ],

    'demo': [],
    'license': 'AGPL-3',

    'installable': True,
    'application': True,
    'auto_install': False,
}

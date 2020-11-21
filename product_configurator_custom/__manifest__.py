# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Product Configurator Custom",
    'version': '1.0',
    'category': 'Hidden',
    'summary': "Configure your products",

    'description': """
    """,

    'depends': ['sale','sale_product_configurator'],
    'data': [
        'views/assets.xml',
        'views/templates.xml',
        'views/sale_views.xml',
    ],
}

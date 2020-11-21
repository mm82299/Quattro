# -*- coding: utf-8 -*-
{
    'name': "Account Payment Report",
    'summary': """
        """,
    'description': """
    """,
    'category': 'Account',
    'version': '0.5.5',
    'depends': ['account'],
    'data': [
        #'data/data.xml',
        'security/ir.model.access.csv',
        'views/report_payment_view.xml',
        'views/account_payment_view.xml',
        'report/report_payment_inherit.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

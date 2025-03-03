# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2023
# -*- encoding: utf-8 -*-
{
    'name': 'Asterisk Plus unlimited edition',
    'version': '1.0',
    'author': 'Odooist',
    'price': 3000,
    'currency': 'EUR',
    'maintainer': 'Odooist',
    'support': 'odooist@gmail.com',
    'license': 'OPL-1',
    'category': 'Phone',
    'summary': 'Asterisk Plus customization for unlimited edition',
    'description': 'Asterisk Plus customization for unlimited edition',
    'depends': ['asterisk_plus'],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'views/settings.xml',
        'views/server.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

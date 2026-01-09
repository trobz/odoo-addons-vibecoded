# -*- coding: utf-8 -*-
{
    'name': 'Force User Session Logout',
    'version': '16.0.1.0.0',
    'category': 'Authentication',
    'summary': 'Administrative tool to force logout of user sessions via API',
    'author': 'Trobz',
    'website': 'https://github.com/trobz/odoo-addons-vibecoded',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
        'auth_signup',
    ],
    'data': [
        'security/security.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
}
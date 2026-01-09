# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Provider: Authorize.Net - Add Card via Customer Profile',
    'version': '16.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 351,
    'summary': "Add payment methods via Customer Profile without validation transactions",
    'description': " ",
    'depends': ['payment_authorize'],
    'data': [
        'views/payment_authorize_add_card_via_customer_profile_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_authorize_add_card_via_customer_profile/static/src/js/payment_form.js',
        ],
    },
    'application': False,
    'license': 'LGPL-3',
    'installable': True,
}

# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Authorize.net Add Card via Customer Profile',
    'version': '16.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Add payment cards to customers via Authorize.net Customer Profile API',
    'description': """
        Add Authorize.net Payment Card via Customer Profile
        ====================================================
        
        This module extends the Authorize.net payment provider to allow adding
        payment cards directly to customer profiles without triggering validation
        transactions.
        
        Features:
        * Direct Customer Profile creation via Authorize.net API
        * Payment token storage for future transactions
        * No validation transaction fees or holds
        * Smart button on Customer (res.partner) form
    """,
    'author': 'Trobz',
    'depends': ['payment_authorize'],
    'data': [
        'views/res_partner_views.xml',
        'views/payment_authorize_add_card_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_authorize_add_card_via_customer_profile/static/src/js/add_card_form.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}

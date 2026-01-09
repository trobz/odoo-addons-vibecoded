# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class AddCardController(http.Controller):

    @http.route('/user/payment_method2/<int:provider_id>/<int:partner_id>',
                type='http', auth='user', website=True)
    def render_add_card_form(self, provider_id, partner_id, **kwargs):
        provider = request.env['payment.provider'].sudo().browse(provider_id).exists()
        partner = request.env['res.partner'].sudo().browse(partner_id).exists()

        if not provider or provider.code != 'authorize':
            raise ValidationError(_('Invalid payment provider'))

        if not partner:
            raise ValidationError(_('Invalid partner'))

        if partner_id != request.env.user.partner_id.id:
            raise ValidationError(_('You can only add cards to your own profile'))

        return request.render('payment_authorize_add_card_via_customer_profile.add_card_form', {
            'provider': provider,
            'partner': partner,
            'page_name': 'add_authorize_card',
        })

    @http.route('/payment/authorize/profile', type='json', auth='user')
    def create_payment_profile(self, provider_id, partner_id, opaque_data):
        """ Create a payment profile from opaque data.

        :param int provider_id: The provider handling the request, as a `payment.provider` id
        :param int partner_id: The partner for whom the profile is created
        :param dict opaque_data: The payment details obfuscated by Authorize.Net
        :return: dict with success status and message
        :rtype: dict
        """
        provider = request.env['payment.provider'].sudo().browse(provider_id).exists()
        partner = request.env['res.partner'].sudo().browse(partner_id).exists()

        if not provider or provider.code != 'authorize':
            return {
                'success': False,
                'error': _('Invalid payment provider')
            }

        if not partner:
            return {
                'success': False,
                'error': _('Invalid partner')
            }

        if partner_id != request.env.user.partner_id.id:
            return {
                'success': False,
                'error': _('You can only add cards to your own profile')
            }

        try:
            result = provider.create_customer_profile_from_opaque_data(partner, opaque_data)

            if not result:
                return {
                    'success': False,
                    'error': _('Failed to create customer profile')
                }

            token_values = {
                'provider_id': provider.id,
                'partner_id': partner.id,
                'authorize_profile': result['profile_id'],
                'provider_ref': result['payment_profile_id'],
                'name': _('%(provider)s: %(details)s', provider=provider.display_name,
                          details='XXXXXXXXXXXX' + result['payment_details']),
                'active': True,
            }

            token = request.env['payment.token'].sudo().create(token_values)

            return {
                'success': True,
                'token_id': token.id,
                'message': _('Payment method added successfully'),
            }

        except Exception as e:
            _logger.error("Error creating payment profile: %s", e)
            return {
                'success': False,
                'error': str(e)
            }

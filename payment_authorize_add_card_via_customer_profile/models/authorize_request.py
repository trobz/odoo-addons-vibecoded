# Part of Odoo. See LICENSE file for full copyright and licensing details.

from uuid import uuid4
import logging

_logger = logging.getLogger(__name__)


from odoo.addons.payment_authorize.models.authorize_request import AuthorizeAPI as BaseAuthorizeAPI


def create_customer_profile_from_opaque_data(self, partner, opaque_data):
    """ Create an Auth.net customer profile from opaque data (nonce).

    Creates a customer profile and payment profile directly using Accept.js
    opaque data without triggering a transaction.

    :param recordset partner: the res.partner record of the customer
    :param dict opaque_data: The payment details obfuscated by Authorize.Net
                              containing 'dataDescriptor' and 'dataValue'
    :return: a dict containing the profile_id, payment_profile_id and last 4 digits
    :rtype: dict
    """
    response = self._make_request('createCustomerProfileRequest', {
        'profile': {
            'merchantCustomerId': ('ODOO-%s-%s' % (partner.id, uuid4().hex[:8]))[:20],
            'email': partner.email or '',
            'paymentProfiles': {
                'customerType': 'individual',
                'payment': {
                    'opaqueData': {
                        'dataDescriptor': opaque_data.get('dataDescriptor'),
                        'dataValue': opaque_data.get('dataValue'),
                    }
                }
            }
        }
    })

    if response.get('err_code'):
        _logger.error(
            "Failed to create customer profile for partner %s: %s",
            partner.id, response.get('err_msg')
        )
        return False

    customer_profile_id = response.get('customerProfileId')
    if not customer_profile_id:
        _logger.error(
            "No customer profile ID returned for partner %s", partner.id
        )
        return False

    payment_profile_ids = response.get('customerPaymentProfileIdList', [])
    if not payment_profile_ids:
        _logger.error(
            "No payment profile ID returned for customer profile %s",
            customer_profile_id
        )
        return False

    payment_profile_id = payment_profile_ids[0]

    response = self._make_request('getCustomerPaymentProfileRequest', {
        'customerProfileId': customer_profile_id,
        'customerPaymentProfileId': payment_profile_id,
    })

    if response.get('err_code'):
        _logger.error(
            "Failed to get payment profile details: %s", response.get('err_msg')
        )
        return {
            'profile_id': customer_profile_id,
            'payment_profile_id': payment_profile_id,
            'payment_details': 'XXXX',
        }

    payment = response.get('paymentProfile', {}).get('payment', {})
    if self.payment_method_type == 'credit_card':
        payment_details = payment.get('creditCard', {}).get('cardNumber', '')[-4:]
    else:
        payment_details = payment.get('bankAccount', {}).get('accountNumber', '')[-4:]

    return {
        'profile_id': customer_profile_id,
        'payment_profile_id': payment_profile_id,
        'payment_details': payment_details or 'XXXX',
    }


BaseAuthorizeAPI.create_customer_profile_from_opaque_data = create_customer_profile_from_opaque_data


from odoo import models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    def create_customer_profile_from_opaque_data(self, partner, opaque_data):
        """ Create a customer profile from opaque data via AuthorizeAPI.

        :param recordset partner: the res.partner record of the customer
        :param dict opaque_data: The payment details obfuscated by Authorize.Net
        :return: a dict with profile details or False
        :rtype: dict or False
        """
        self.ensure_one()
        from odoo.addons.payment_authorize.models.authorize_request import AuthorizeAPI
        api = AuthorizeAPI(self)
        return api.create_customer_profile_from_opaque_data(partner, opaque_data)

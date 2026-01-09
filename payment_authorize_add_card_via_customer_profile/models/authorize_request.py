# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from uuid import uuid4

from odoo import _
from odoo.exceptions import UserError
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_authorize.models.authorize_request import AuthorizeAPI

_logger = logging.getLogger(__name__)


def create_customer_profile_from_opaque_data(self, partner, opaque_data):
    """Create an Auth.net customer profile and payment profile from opaque data.

    Creates a customer profile and payment profile directly from Accept.js opaque data
    without requiring a validation transaction. This approach allows adding payment
    methods without triggering a 0.01$ transaction.

    This function makes 2 calls to the authorize API:
    1. Create or get the customer profile
    2. Create a payment profile with the opaque data
    3. Get payment profile details to obtain the card number

    :param record partner: the res.partner record of the customer
    :param dict opaque_data: The payment details obfuscated by Authorize.Net (dataDescriptor, dataValue)

    :return: a dict containing the profile_id and payment_profile_id of the
                newly created customer profile and payment profile as well as the
                last digits of the card number and expiration date
    :rtype: dict
    """
    merchant_customer_id = ("ODOO-%s-%s" % (partner.id, uuid4().hex[:8]))[:20]

    customer_profile = self._get_or_create_customer_profile(partner, merchant_customer_id)
    customer_profile_id = customer_profile

    response = self._make_request(
        "createCustomerPaymentProfileRequest",
        {
            "customerProfileId": customer_profile_id,
            "paymentProfile": {
                "payment": {
                    "opaqueData": {
                        "dataDescriptor": opaque_data.get("dataDescriptor"),
                        "dataValue": opaque_data.get("dataValue"),
                    }
                },
                "defaultPaymentProfile": False,
            },
        },
    )

    if response.get("err_code"):
        _logger.warning(
            "unable to create customer payment profile from opaque data, "
            "partner id: %(partner_id)s, error: %(error)s",
            {
                "partner_id": partner.id,
                "error": response.get("err_msg"),
            },
        )
        return False

    payment_profile_id = response.get("customerPaymentProfileId")

    response = self._make_request(
        "getCustomerPaymentProfileRequest",
        {
            "customerProfileId": customer_profile_id,
            "customerPaymentProfileId": payment_profile_id,
            "unmaskExpirationDate": True,
        },
    )

    if response.get("err_code"):
        _logger.warning(
            "unable to get customer payment profile details, "
            "partner id: %(partner_id)s, error: %(error)s",
            {
                "partner_id": partner.id,
                "error": response.get("err_msg"),
            },
        )
        return False

    payment = response.get("paymentProfile", {}).get("payment", {})
    expDate = payment.get("creditCard", {}).get("expirationDate", "").split("-")
    year = expDate and expDate[0][-2:] or ""
    month = expDate and expDate[1] or ""
    expirationDate = f"{month}/{year}"

    res = {
        "profile_id": customer_profile_id,
        "payment_profile_id": payment_profile_id,
        "payment_details": payment.get("creditCard", {}).get("cardNumber")[-4:]
        if self.payment_method_type == "credit_card"
        else payment.get("bankAccount", {}).get("accountNumber")[-4:],
        "expirationDate": expirationDate,
    }

    return res


def _get_or_create_customer_profile(self, partner, merchant_customer_id):
    """Get or create a customer profile in Authorize.net.

    First tries to get the customer profile by merchant customer ID and email.
    If not found, creates a new customer profile.

    :param record partner: the res.partner record of the customer
    :param str merchant_customer_id: the merchant customer ID (max 20 chars)

    :return: the customer profile ID
    :rtype: str
    """
    response = self._make_request(
        "getCustomerProfileRequest",
        {
            "merchantCustomerId": merchant_customer_id,
            "email": partner.email or "",
        },
    )

    if not response.get("err_code"):
        customer_profile_id = response.get("profile", {}).get("customerProfileId")
        if customer_profile_id:
            _logger.info(
                "Found existing customer profile for partner %(partner_id)s: %(profile_id)s",
                {
                    "partner_id": partner.id,
                    "profile_id": customer_profile_id,
                },
            )
            return customer_profile_id

    response = self._make_request(
        "createCustomerProfileRequest",
        {
            "profile": {
                "merchantCustomerId": merchant_customer_id,
                "email": partner.email or "",
                "description": partner.name or "",
            }
        },
    )

    if response.get("err_code"):
        _logger.error(
            "unable to create customer profile, partner id: %(partner_id)s, error: %(error)s",
            {
                "partner_id": partner.id,
                "error": response.get("err_msg"),
            },
        )
        raise UserError(
            _(
                "Unable to create customer profile in Authorize.net: %s"
            ) % response.get("err_msg")
        )

    customer_profile_id = response.get("customerProfileId")
    _logger.info(
        "Created new customer profile for partner %(partner_id)s: %(profile_id)s",
        {
            "partner_id": partner.id,
            "profile_id": customer_profile_id,
        },
    )

    return customer_profile_id


AuthorizeAPI.create_customer_profile_from_opaque_data = create_customer_profile_from_opaque_data
AuthorizeAPI._get_or_create_customer_profile = _get_or_create_customer_profile

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug.urls import url_encode

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_authorize.controllers.main import AuthorizeController


class AuthorizeAddCardController(AuthorizeController):
    @http.route(
        ["/user/payment_method2/<model('res.partner'):partner>"],
        type="http",
        auth="user",
        methods=["GET"],
        website=True,
    )
    def payment_method_input2(self, partner, **kwargs):
        company_id = kwargs.get("company_id")
        if company_id is None:
            company_id = request.env.company.id
        providers_sudo = (
            request.env["payment.provider"]
            .sudo()
            ._get_compatible_providers(
                int(company_id),
                partner.id,
                0.0,
                force_tokenization=True,
                is_validation=True,
            )
        )
        payment_tokens = partner.payment_token_ids
        payment_tokens |= partner.commercial_partner_id.sudo().payment_token_ids
        access_token = payment_utils.generate_access_token(partner.id, None, None)

        action_id = kwargs.get("action", False)
        if kwargs.get("model", False) in ["sale.order", "account.move", "res.partner"]:
            request.env[kwargs.get("model")].browse(int(kwargs.get("id")))
            if kwargs.get("model", False) == "sale.order":
                action_xml_id = "sale.action_orders"
            elif kwargs.get("model", False) == "account.move":
                action_xml_id = "account.action_move_out_invoice_type"
            elif kwargs.get("model", False) == "res.partner":
                action_xml_id = "base.action_partner_form"
            action_id = request.env.ref(action_xml_id).id
            kwargs.update(
                {
                    "action": action_id,
                }
            )

        return_url = request.params.get(
            "redirect",
            "/user/payment_method2/%s/?%s" % (partner.id, url_encode(dict(kwargs))),
        )
        values = dict(kwargs)
        values.update(
            {
                "tokens": payment_tokens,
                "providers": providers_sudo,
                "landing_route": return_url,
                "access_token": access_token,
                "transaction_route": "/payment/profile",
                "reference_prefix": payment_utils.singularize_reference_prefix(
                    prefix="validation"
                ),
                "partner_id": partner.id,
            }
        )
        return request.render(
            "payment_authorize_add_card_via_customer_profile.payment_methods2", values
        )

    @http.route(
        ["/payment/profile"],
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def payment_profile(self, **kwargs):
        provider_id = kwargs.get("provider_id")
        partner_id = kwargs.get("partner_id")
        opaque_data = kwargs.get("opaque_data")

        if not provider_id or not partner_id or not opaque_data:
            raise ValidationError(
                "Missing required parameters: provider_id, partner_id, or opaque_data"
            )

        provider_sudo = request.env["payment.provider"].sudo().browse(int(provider_id))
        if provider_sudo.code != "authorize":
            raise ValidationError("Only Authorize.net provider is supported")

        partner_sudo = request.env["res.partner"].sudo().browse(int(partner_id))
        if not partner_sudo.exists():
            raise ValidationError("Partner not found")

        api = provider_sudo._authorize_get_api()

        profile_data = api.create_customer_profile_from_opaque_data(
            partner_sudo, opaque_data
        )

        if not profile_data:
            raise ValidationError(
                "Failed to create customer profile from opaque data in Authorize.net"
            )

        token_values = {
            "provider_id": provider_sudo.id,
            "partner_id": partner_sudo.id,
            "authorize_profile": profile_data.get("profile_id"),
            "provider_ref": profile_data.get("payment_profile_id"),
            "payment_details": profile_data.get("payment_details"),
            "expiration_date": profile_data.get("expirationDate"),
        }

        token = (
            request.env["payment.token"]
            .sudo()
            .with_context(create_from_profile=True)
            .create(token_values)
        )

        return {
            "success": True,
            "token_id": token.id,
            "token_name": token.display_name,
        }

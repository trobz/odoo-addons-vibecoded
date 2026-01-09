/* global Accept */
odoo.define("payment_authorize_add_card_via_customer_profile.payment_form", (require) => {
    "use strict";

    const core = require("web.core");
    const { loadJS } = require("@web/core/assets");

    const manageForm = require("payment.manage_form");

    const _t = core._t;

    const authorizeAddCardMixin = {
        _responseHandlerAddCard: function (providerId, response) {
            if (response.messages.resultCode === "Error") {
                let error = "";
                response.messages.message.forEach(
                    (msg) => (error += `${msg.code}: ${msg.text}\n`)
                );
                this._displayError(
                    _t("Server Error"),
                    _t("We are not able to add your payment method."),
                    error
                );
                return Promise.resolve();
            }

            return this._rpc({
                route: "/payment/profile",
                params: {
                    provider_id: providerId,
                    partner_id: this.txContext.partnerId,
                    opaque_data: response.opaqueData,
                },
            }).then((result) => {
                window.location.reload();
            }).guardedCatch((error) => {
                error.event.preventDefault();
                this._displayError(
                    _t("Server Error"),
                    _t("We are not able to add your payment method."),
                    error.message.data.message
                );
            });
        },

        _processPaymentForAddCard: function (code, paymentOptionId, flow) {
            if (code !== "authorize") {
                return this._super(...arguments);
            }

            if (!this._validateFormInputs(paymentOptionId)) {
                this._enableButton();
                $("body").unblock();
                return Promise.resolve();
            }

            const secureData = {
                authData: {
                    apiLoginID: this.authorizeInfo.login_id,
                    clientKey: this.authorizeInfo.client_key,
                },
                ...this._getPaymentDetails(paymentOptionId),
            };

            return Accept.dispatchData(
                secureData,
                (response) => this._responseHandlerAddCard(paymentOptionId, response)
            );
        },

        _prepareInlineFormAddCard: function (code, paymentOptionId, flow) {
            if (code !== "authorize") {
                return this._super(...arguments);
            }

            let acceptJSUrl = "https://js.authorize.net/v1/Accept.js";
            return this._rpc({
                route: "/payment/authorize/get_provider_info",
                params: {
                    provider_id: paymentOptionId,
                },
            }).then((providerInfo) => {
                if (providerInfo.state !== "enabled") {
                    acceptJSUrl = "https://jstest.authorize.net/v1/Accept.js";
                }
                this.authorizeInfo = providerInfo;
            }).then(() => {
                loadJS(acceptJSUrl);
            }).guardedCatch((error) => {
                error.event.preventDefault();
                this._displayError(
                    _t("Server Error"),
                    _t("An error occurred when displayed this payment form."),
                    error.message.data.message
                );
            });
        },
    };

    manageForm.include(authorizeAddCardMixin);
});

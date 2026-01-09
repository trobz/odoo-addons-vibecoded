/* global Accept */
odoo.define('payment_authorize_add_card_via_customer_profile.add_card_form', require => {
    'use strict';

    const core = require('web.core');
    const { loadJS } = require('@web/core/assets');
    const rpc = require('web.rpc');

    const _t = core._t;

    const AddCardForm = {
        
        start: function () {
            const providerId = $('#o_add_card_provider_id').val();
            const partnerId = $('#o_add_card_partner_id').val();
            let acceptJSUrl = 'https://js.authorize.net/v1/Accept.js';

            rpc.query({
                route: '/payment/authorize/get_provider_info',
                params: { provider_id: providerId },
            }).then(providerInfo => {
                if (providerInfo.state !== 'enabled') {
                    acceptJSUrl = 'https://jstest.authorize.net/v1/Accept.js';
                }
                this.authorizeInfo = providerInfo;
                
                return loadJS(acceptJSUrl);
            }).then(() => {
                $('#o_add_card_submit').on('click', this._onSubmitClick.bind(this));
            }).guardedCatch((error) => {
                $('#o_add_card_error').text(_t('Failed to load payment form: ') + error.message).show();
            });

            return this._super.apply(this, arguments);
        },

        _onSubmitClick: function (e) {
            e.preventDefault();
            
            const card = $('#o_authorize_card').val().replace(/ /g, '');
            const month = $('#o_authorize_month').val();
            const year = $('#o_authorize_year').val();
            const code = $('#o_authorize_code').val();

            if (!card || !month || !year || !code) {
                $('#o_add_card_error').text(_t('Please fill in all card details')).show();
                return;
            }

            $('#o_add_card_submit').prop('disabled', true);
            $('#o_add_card_error').hide();

            const secureData = {
                authData: {
                    apiLoginID: this.authorizeInfo.login_id,
                    clientKey: this.authorizeInfo.client_key,
                },
                cardData: {
                    cardNumber: card,
                    month: month,
                    year: year,
                    cardCode: code,
                },
            };

            Accept.dispatchData(secureData, response => this._handleResponse(response));
        },

        _handleResponse: function (response) {
            if (response.messages.resultCode === 'Error') {
                let error = '';
                response.messages.message.forEach(msg => {
                    error += `${msg.code}: ${msg.text}\n`;
                });
                $('#o_add_card_error').text(error).show();
                $('#o_add_card_submit').prop('disabled', false);
                return;
            }

            const providerId = $('#o_add_card_provider_id').val();
            const partnerId = $('#o_add_card_partner_id').val();

            rpc.query({
                route: '/payment/authorize/profile',
                params: {
                    provider_id: parseInt(providerId),
                    partner_id: parseInt(partnerId),
                    opaque_data: response.opaqueData,
                },
            }).then(result => {
                if (result.success) {
                    $('#o_add_card_form').hide();
                    $('#o_add_card_success').show();
                } else {
                    $('#o_add_card_error').text(result.error || _t('Failed to add payment method')).show();
                    $('#o_add_card_submit').prop('disabled', false);
                }
            }).guardedCatch((error) => {
                $('#o_add_card_error').text(error.message.data.message || _t('Server error')).show();
                $('#o_add_card_submit').prop('disabled', false);
            });
        },
    };

    return AddCardForm;
});

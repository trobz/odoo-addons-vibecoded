# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models, fields
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_token_count = fields.Integer(
        string='Payment Token Count',
        compute='_compute_payment_token_count'
    )

    def _compute_payment_token_count(self):
        for partner in self:
            partner.payment_token_count = self.env['payment.token'].search_count([
                ('partner_id', '=', partner.id),
                ('provider_code', '=', 'authorize'),
                ('active', '=', True)
            ])

    def action_view_payment_tokens(self):
        action = {
            'name': _('Authorize.net Payment Methods'),
            'type': 'ir.actions.act_window',
            'res_model': 'payment.token',
            'view_mode': 'tree,form',
            'domain': [
                ('partner_id', '=', self.id),
                ('provider_code', '=', 'authorize'),
            ],
            'context': {'default_partner_id': self.id},
        }
        return action

    def action_add_authorize_card(self):
        providers = self.env['payment.provider'].search([
            ('code', '=', 'authorize'),
            ('state', 'in', ['enabled', 'test']),
        ], limit=1)

        if not providers:
            raise UserError(_(
                'No active Authorize.net payment provider found. '
                'Please configure an Authorize.net provider first.'
            ))

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': f'/user/payment_method2/{providers.id}/{self.id}',
        }

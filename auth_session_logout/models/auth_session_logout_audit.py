from odoo import fields, models


class AuthSessionLogoutAudit(models.Model):
    _name = 'auth.session.logout.audit'
    _description = 'Force Session Logout Audit Log'
    _order = 'create_date desc'

    target_user_id = fields.Many2one(
        'res.users',
        string='Target User',
        ondelete='set null',
        readonly=True,
    )
    target_user_login = fields.Char(
        related='target_user_id.login',
        string='Target User Login',
        readonly=True,
        store=True,
    )
    request_ip = fields.Char(
        string='Request IP Address',
        readonly=True,
    )
    user_agent = fields.Char(
        string='User Agent',
        readonly=True,
    )
    status = fields.Selection([
        ('success', 'Success'),
        ('unauthorized', 'Unauthorized'),
        ('user_not_found', 'User Not Found'),
        ('error', 'Error'),
    ], string='Status', readonly=True, required=True, default='success')
    error_message = fields.Text(
        string='Error Message',
        readonly=True,
    )
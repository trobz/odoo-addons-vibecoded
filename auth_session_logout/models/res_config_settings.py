from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_session_logout_token = fields.Char(
        string='Force Logout Token',
        config_parameter='auth_session_logout.token',
        help='Secure token used to authenticate force logout API requests'
    )

    def set_values(self):
        """Override to restrict access to system administrators"""
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(_("Only administrators can modify the force logout token."))
        
        # Auto-generate token if empty
        if not self.auth_session_logout_token:
            import secrets
            self.auth_session_logout_token = secrets.token_urlsafe(32)
        
        super(ResConfigSettings, self).set_values()

    @api.model
    def get_values(self):
        """Override to restrict access to system administrators"""
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(_("Only administrators can view the force logout token."))
        
        res = super(ResConfigSettings, self).get_values()
        return res

    def action_generate_token(self):
        """Generate a new secure token"""
        import secrets
        self.auth_session_logout_token = secrets.token_urlsafe(32)
        return {
            'type': 'ir.actions.do_nothing',
        }
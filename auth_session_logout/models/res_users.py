from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    force_logout_count = fields.Integer(
        string='Force Logout Count',
        help='Number of times this user has been force logged out',
        readonly=True,
        default=0,
    )

    def write(self, vals):
        """Override to track force logout operations"""
        result = super(ResUsers, self).write(vals)
        
        # Check if this is a force logout operation (auth_time update)
        if 'auth_time' in vals and len(vals) == 1:
            for user in self:
                user.force_logout_count += 1
        
        return result
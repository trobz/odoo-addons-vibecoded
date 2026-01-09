import json
import secrets
import logging

from odoo import http, _, tools
from odoo.http import request, content_disposition
from odoo.exceptions import AccessDenied, UserError

_logger = logging.getLogger(__name__)


class SessionLogoutController(http.Controller):

    def _validate_token(self, token):
        """Validate the provided token against system parameter"""
        if not token:
            return False
        
        system_token = request.env['ir.config_parameter'].sudo().get_param('auth_session_logout.token')
        if not system_token:
            _logger.error("Logout token not configured")
            return False
        
        return secrets.compare_digest(token, system_token)

    def _find_user(self, user_identifier):
        """Find user by login or email (case insensitive)"""
        if not user_identifier:
            return None
        
        # Try by login first (case insensitive)
        user = request.env['res.users'].sudo().search([
            ('login', '=ilike', user_identifier)
        ], limit=1)
        
        if not user:
            # Try by email (case insensitive)
            user = request.env['res.users'].sudo().search([
                ('email', '=ilike', user_identifier)
            ], limit=1)
        
        return user

    def _force_user_logout(self, user):
        """Force logout of all sessions for the user by updating auth_time"""
        try:
            # Update auth_time to invalidate all existing sessions
            # This is the same mechanism used when user changes password
            user.sudo().write({'auth_time': tools.datetime.utcnow()})
            
            # Create audit log
            request.env['auth.session.logout.audit'].sudo().create({
                'target_user_id': user.id,
                'request_ip': request.httprequest.environ.get('REMOTE_ADDR', 'Unknown'),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', '')[:200],
                'status': 'success',
            })
            
            _logger.info(f"Force logout triggered for user {user.login} from IP {request.httprequest.environ.get('REMOTE_ADDR')}")
            return True
            
        except Exception as e:
            _logger.error(f"Failed to force logout for user {user.login}: {str(e)}")
            
            # Create audit log for failure
            request.env['auth.session.logout.audit'].sudo().create({
                'target_user_id': user.id,
                'request_ip': request.httprequest.environ.get('REMOTE_ADDR', 'Unknown'),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', '')[:200],
                'status': 'error',
                'error_message': str(e)[:500],
            })
            return False

    @http.route('/web/session/force_logout', type='http', auth='none', methods=['GET'], csrf=False)
    def force_logout(self, token=None, user=None, **kwargs):
        """Force logout of user sessions
        
        Args:
            token (str): Authentication token configured in system parameters
            user (str): User login or email to logout
        
        Returns:
            JSON response with success/error status
        """
        try:
            # Validate token
            if not self._validate_token(token):
                # Create audit log for failed authentication
                request.env['auth.session.logout.audit'].sudo().create({
                    'request_ip': request.httprequest.environ.get('REMOTE_ADDR', 'Unknown'),
                    'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', '')[:200],
                    'status': 'unauthorized',
                    'error_message': 'Invalid or missing token',
                })
                
                return request.make_json_response({
                    'error': 'Unauthorized',
                    'message': 'Invalid or missing authentication token'
                }, status=401)

            # Find user
            target_user = self._find_user(user)
            if not target_user:
                # Create audit log for user not found
                request.env['auth.session.logout.audit'].sudo().create({
                    'request_ip': request.httprequest.environ.get('REMOTE_ADDR', 'Unknown'),
                    'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', '')[:200],
                    'status': 'user_not_found',
                    'error_message': f'User not found: {user}',
                })
                
                return request.make_json_response({
                    'error': 'User not found',
                    'message': f'User with login or email "{user}" not found'
                }, status=404)

            # Force logout
            if self._force_user_logout(target_user):
                return request.make_json_response({
                    'success': True,
                    'message': f'User "{target_user.login}" has been logged out successfully'
                })
            else:
                return request.make_json_response({
                    'error': 'Internal error',
                    'message': 'Failed to logout user. Please check logs for details.'
                }, status=500)

        except Exception as e:
            _logger.error(f"Unexpected error in force_logout: {str(e)}")
            
            # Create audit log for unexpected error
            request.env['auth.session.logout.audit'].sudo().create({
                'request_ip': request.httprequest.environ.get('REMOTE_ADDR', 'Unknown'),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', '')[:200],
                'status': 'error',
                'error_message': str(e)[:500],
            })
            
            return request.make_json_response({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred. Please contact administrator.'
            }, status=500)
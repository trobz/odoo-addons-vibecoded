import json
import unittest

from odoo.tests import common
from odoo.tools import ustr


class TestForceLogout(common.HttpCase):

    def setUp(self):
        super(TestForceLogout, self).setUp()
        self.test_token = 'test_token_12345'
        self.env['ir.config_parameter'].sudo().set_param('auth_session_logout.token', self.test_token)
        
        # Create test user
        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'email': 'test@example.com',
            'password': 'test_password',
        })

    def test_force_logout_success(self):
        """Test successful force logout"""
        response = self.url_open(
            '/web/session/force_logout',
            params={
                'token': self.test_token,
                'user': 'testuser'
            }
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('logged out successfully', data.get('message', ''))

    def test_force_logout_with_email(self):
        """Test force logout using email"""
        response = self.url_open(
            '/web/session/force_logout',
            params={
                'token': self.test_token,
                'user': 'test@example.com'
            }
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get('success'))

    def test_force_logout_invalid_token(self):
        """Test force logout with invalid token"""
        response = self.url_open(
            '/web/session/force_logout',
            params={
                'token': 'invalid_token',
                'user': 'testuser'
            }
        )
        self.assertEqual(response.status_code, 401)
        
        data = response.json()
        self.assertEqual(data.get('error'), 'Unauthorized')

    def test_force_logout_missing_token(self):
        """Test force logout without token"""
        response = self.url_open(
            '/web/session/force_logout',
            params={
                'user': 'testuser'
            }
        )
        self.assertEqual(response.status_code, 401)
        
        data = response.json()
        self.assertEqual(data.get('error'), 'Unauthorized')

    def test_force_logout_user_not_found(self):
        """Test force logout with non-existent user"""
        response = self.url_open(
            '/web/session/force_logout',
            params={
                'token': self.test_token,
                'user': 'nonexistent@example.com'
            }
        )
        self.assertEqual(response.status_code, 404)
        
        data = response.json()
        self.assertEqual(data.get('error'), 'User not found')

    def test_force_logout_case_insensitive(self):
        """Test that user lookup is case insensitive"""
        response = self.url_open(
            '/web/session/force_logout',
            params={
                'token': self.test_token,
                'user': 'TESTUSER'
            }
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get('success'))

    def test_audit_log_creation(self):
        """Test that audit logs are created"""
        self.url_open(
            '/web/session/force_logout',
            params={
                'token': self.test_token,
                'user': 'testuser'
            }
        )
        
        audit_logs = self.env['auth.session.logout.audit'].search([
            ('target_user_id', '=', self.test_user.id)
        ])
        self.assertTrue(len(audit_logs) > 0)
        self.assertEqual(audit_logs[0].status, 'success')

    def test_force_logout_count_increment(self):
        """Test that force logout count is incremented"""
        initial_count = self.test_user.force_logout_count
        
        self.url_open(
            '/web/session/force_logout',
            params={
                'token': self.test_token,
                'user': 'testuser'
            }
        )
        
        self.test_user.refresh()
        self.assertEqual(self.test_user.force_logout_count, initial_count + 1)


@common.tagged('post_install', '-at_install')
class TestForceLogoutIntegration(common.HttpCase):
    """Integration tests for force logout functionality"""

    def setUp(self):
        super(TestForceLogoutIntegration, self).setUp()
        self.test_token = 'integration_test_token'
        self.env['ir.config_parameter'].sudo().set_param('auth_session_logout.token', self.test_token)

    def test_session_invalidation(self):
        """Test that user sessions are actually invalidated"""
        # This test would require more complex session setup
        # For now, we verify the auth_time is updated
        user = self.env['res.users'].search([('login', '=', 'demo')])
        if user:
            old_auth_time = user.auth_time
            
            response = self.url_open(
                '/web/session/force_logout',
                params={
                    'token': self.test_token,
                    'user': 'demo'
                }
            )
            
            self.assertEqual(response.status_code, 200)
            user.refresh()
            self.assertNotEqual(user.auth_time, old_auth_time)
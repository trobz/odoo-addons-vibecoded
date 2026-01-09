# Force User Session Logout

## Overview

This module provides an administrative API endpoint to force logout of specific user sessions in Odoo. It's designed for system administrators who need to immediately terminate user sessions for security or administrative purposes.

## Features

- **Secure API Endpoint**: `/web/session/force_logout` with token-based authentication
- **User Identification**: Support for both login and email (case-insensitive)
- **Session Invalidation**: Uses the same mechanism as password changes to invalidate sessions
- **Audit Logging**: Comprehensive audit trail of all logout operations
- **Admin Interface**: Token management through Odoo settings
- **Security Controls**: Token access restricted to system administrators

## Configuration

### 1. Install the Module

```bash
# Using Odoo CLI
odoo -d database_name -i auth_session_logout

# Or through Apps menu in Odoo
```

### 2. Configure the Token

1. Go to **Settings** → **General Settings**
2. Scroll to the **Force Session Logout** section
3. Click **Generate Token** to create a secure authentication token
4. Save the settings

> **Important**: Only users with **Administration/Settings** access can view or modify the token.

## API Usage

### Endpoint
```
GET /web/session/force_logout
```

### Parameters
- `token` (required): The secure token configured in settings
- `user` (required): User login or email to logout

### Success Response (200)
```json
{
  "success": true,
  "message": "User \"john.doe\" has been logged out successfully"
}
```

### Error Responses

**Unauthorized (401)**
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing authentication token"
}
```

**User Not Found (404)**
```json
{
  "error": "User not found",
  "message": "User with login or email \"unknown@example.com\" not found"
}
```

**Internal Error (500)**
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred. Please contact administrator."
}
```

## Usage Examples

### Using curl
```bash
curl -X GET "https://your-odoo.com/web/session/force_logout?token=your_secure_token&user=john.doe@example.com"
```

### Using Python
```python
import requests

url = "https://your-odoo.com/web/session/force_logout"
params = {
    'token': 'your_secure_token',
    'user': 'john.doe@example.com'
}

response = requests.get(url, params=params)
print(response.json())
```

### Using JavaScript
```javascript
const url = "https://your-odoo.com/web/session/force_logout";
const params = new URLSearchParams({
    token: 'your_secure_token',
    user: 'john.doe@example.com'
});

fetch(`${url}?${params}`)
    .then(response => response.json())
    .then(data => console.log(data));
```

## Security Considerations

### Token Security
- Tokens are stored in system parameters with restricted access
- Only users in the Administration/Settings group can view/modify tokens
- Tokens are generated using cryptographically secure random methods
- Minimum 32-character length for generated tokens

### Network Security
- **Always use HTTPS** in production environments
- Consider IP whitelisting for the API endpoint
- Monitor audit logs for unauthorized access attempts

### Audit Trail
All API calls are logged with:
- Request timestamp
- Source IP address
- User agent string
- Target user (if found)
- Operation status (success/unauthorized/error)
- Error messages (if applicable)

## Audit Monitoring

Access audit logs through:
- **Settings** → **Users & Companies** → **Force Logout Audit**

Or directly via the database:
```sql
SELECT 
    create_date,
    target_user_login,
    request_ip,
    status,
    error_message
FROM auth_session_logout_audit 
ORDER BY create_date DESC;
```

## Session Invalidation Mechanism

The module uses Odoo's built-in session security by updating the `auth_time` field on the user record. This is the same mechanism used when:
- A user changes their password
- The system forces password expiration

All active sessions for the user become invalid immediately after the `auth_time` update.

## Troubleshooting

### Common Issues

**"Unauthorized" Response**
- Verify the token is correctly configured in settings
- Ensure the token is URL-encoded in your request
- Check for trailing/leading spaces in the token

**"User Not Found" Response**
- Verify the user exists in the system
- Check for typos in the login/email
- Remember that the search is case-insensitive

**"Internal Error" Response**
- Check Odoo server logs for detailed error information
- Verify the user has valid permissions
- Ensure the database connection is working

### Logging
Enable debug logging to troubleshoot:
```python
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
```

## Integration Examples

### Integration with External Identity Provider
```python
# When external IdP reports security incident
def handle_security_breach(user_email):
    odoo_url = "https://your-odoo.com/web/session/force_logout"
    token = os.environ.get('ODOO_LOGOUT_TOKEN')
    
    response = requests.get(odoo_url, params={
        'token': token,
        'user': user_email
    })
    
    if response.status_code == 200:
        print(f"Successfully logged out {user_email}")
    else:
        print(f"Failed to logout {user_email}: {response.text}")
```

### Bulk Logout Script
```python
def logout_multiple_users(user_list, token):
    base_url = "https://your-odoo.com/web/session/force_logout"
    results = []
    
    for user in user_list:
        response = requests.get(base_url, params={
            'token': token,
            'user': user
        })
        results.append({
            'user': user,
            'status': response.status_code,
            'response': response.json()
        })
    
    return results
```

## Technical Details

### Database Schema
- `auth.session.logout.audit`: Audit log table
- `res.users`: Extended with `force_logout_count` field
- `ir.config_parameter`: Stores the authentication token

### Session Invalidation
The module updates the `auth_time` field on the user record, which invalidates all existing sessions. This is Odoo's standard mechanism for session invalidation.

### Performance Impact
- Minimal database overhead (single user record update)
- Efficient audit logging (async when possible)
- No impact on users not being logged out

## License

This module is licensed under AGPL-3.0. See LICENSE file for details.

## Support

For support and contributions:
- GitHub: https://github.com/trobz/odoo-addons-vibecoded
- Issues: https://github.com/trobz/odoo-addons-vibecoded/issues

---

**Version**: 16.0.1.0.0  
**Author**: Trobz  
**License**: AGPL-3
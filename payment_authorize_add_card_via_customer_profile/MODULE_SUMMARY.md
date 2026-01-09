# Module Summary: payment_authorize_add_card_via_customer_profile

## Location
`/home/xavie/code/trobz/odoo-addons-vibecoded/payment_authorize_add_card_via_customer_profile`

## Module Structure

```
payment_authorize_add_card_via_customer_profile/
├── __init__.py
├── __manifest__.py
├── README.md
├── controllers/
│   ├── __init__.py
│   └── main.py
├── i18n/
│   └── payment_authorize_add_card_via_customer_profile.pot
├── models/
│   ├── __init__.py
│   ├── authorize_request.py
│   └── res_partner.py
├── static/
│   └── src/
│       └── js/
│           └── add_card_form.js
└── views/
    ├── payment_authorize_add_card_templates.xml
    └── res_partner_views.xml
```

## File Descriptions

### Core Files

1. **`__manifest__.py`**
   - Module metadata and configuration
   - Version: 16.0.1.0.0
   - Dependencies: payment_authorize
   - Assets: Frontend JavaScript for card form

2. **`README.md`**
   - Complete documentation of module features, usage, and technical details

### Models (`models/`)

3. **`models/authorize_request.py`**
   - Extends the base AuthorizeAPI class
   - Adds `create_customer_profile_from_opaque_data()` method
   - Creates customer profiles via Authorize.net API without transactions
   - Retrieves last 4 digits of card for token naming

4. **`models/res_partner.py`**
   - Extends res.partner model
   - Adds `payment_token_count` computed field
   - Adds `action_view_payment_tokens()` - view all tokens for customer
   - Adds `action_add_authorize_card()` - redirect to add card form

### Controllers (`controllers/`)

5. **`controllers/main.py`**
   - Route `/user/payment_method2/<provider_id>/<partner_id>` - Renders add card form
   - Route `/payment/authorize/profile` (POST) - Creates payment profile from opaque data
   - Security: Validates user can only add cards to their own profile

### Frontend (`static/`)

6. **`static/src/js/add_card_form.js`**
   - Loads Authorize.net Accept.js library dynamically
   - Handles card form validation
   - Tokenizes card data via Accept.dispatchData()
   - Posts opaque data to backend controller
   - Displays success/error messages

### Views (`views/`)

7. **`views/res_partner_views.xml`**
   - Smart button on partner form showing payment token count
   - "Add Authorize.net Card" button in partner form header
   - Only visible for customers (customer_rank > 0)

8. **`views/payment_authorize_add_card_templates.xml`**
   - Card input form template
   - Portal layout integration
   - Includes security information
   - Success/error message display

## Key Features Implemented

### 1. Direct Customer Profile Creation
- Uses Authorize.net `createCustomerProfileRequest` API
- Accepts opaque data (dataDescriptor + dataValue) from Accept.js
- No validation transaction required

### 2. Payment Token Storage
- Creates `payment.token` record in Odoo
- Links to partner and provider
- Stores authorize_profile and provider_ref
- Token name includes last 4 digits of card

### 3. User Interface
- Smart button on customer form shows token count
- "Add Authorize.net Card" button opens form
- Clean, responsive form with Bootstrap styling
- Security information displayed to users

### 4. Security
- PCI-DSS compliant: No raw card data stored
- Accept.js tokenization on client-side
- Access control: Users can only add cards to their own profile
- HTTPS required for Accept.js

### 5. API Flow
```
User Clicks "Add Card" 
    → Form Renders 
    → User Enters Card Details 
    → Accept.js Tokenizes (dataDescriptor + dataValue)
    → POST to /payment/authorize/profile
    → Backend calls Authorize.net API
    → createCustomerProfileRequest
    → getCustomerPaymentProfileRequest
    → Create payment.token in Odoo
    → Return success
```

## Differences from payment_authorize_backend

| Feature | payment_authorize_backend | This Module |
|---------|--------------------------|-------------|
| Validation Transaction | $0.01 charge | None |
| API Method | createCustomerProfileFromTransactionRequest | createCustomerProfileRequest |
| Input | transaction_id | opaque_data (nonce) |
| Fees | Yes (validation charge) | No |

## Installation

```bash
# In Odoo directory
./odoo-bin -i payment_authorize_add_card_via_customer_profile -d your_database
```

Or via Apps menu in Odoo interface.

## Usage

1. Configure Authorize.net provider (payment_authorize module)
2. Navigate to a customer/partner form
3. Click "Add Authorize.net Card" button
4. Enter card details
5. Click "Add Payment Method"
6. Card is saved and available for future transactions

## Testing Checklist

- [ ] Module installs without errors
- [ ] Smart button appears on customer form
- [ ] "Add Authorize.net Card" button opens form
- [ ] Form validates required fields
- [ ] Accept.js loads correctly
- [ ] Card tokenization works
- [ ] Customer profile created in Authorize.net
- [ ] Payment token created in Odoo
- [ ] Last 4 digits displayed correctly
- [ ] Security messages displayed
- [ ] Error handling works
- [ ] Users cannot add cards to other customers
- [ ] Tokens count updates correctly

## Dependencies

- Odoo 16.0
- `payment` (base module)
- `payment_authorize` (native Odoo module)
- Authorize.net merchant account with API credentials
- Accept.js public client key

## Notes

- The module uses Python monkey-patching to extend the AuthorizeAPI class
- All card data is tokenized client-side by Accept.js
- No raw card numbers are stored or transmitted to Odoo
- Customer profiles are created directly in Authorize.net
- Payment tokens can be used for standard payment transactions

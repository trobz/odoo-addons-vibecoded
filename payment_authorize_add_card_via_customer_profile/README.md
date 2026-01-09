# Payment Authorize.net Add Card via Customer Profile

## Overview

This Odoo module extends the Authorize.net payment provider to allow adding payment cards directly to customer profiles without triggering validation transactions.

## Features

- **Direct Customer Profile Creation**: Create Authorize.net customer profiles using the Accept.js opaque data tokenization
- **No Validation Transactions**: Skip the $0.01 validation transaction to avoid fees and holds
- **Payment Token Storage**: Save payment tokens in Odoo for future real transactions
- **Smart Button**: Easy access to add cards from the Customer (res.partner) form
- **Secure**: Raw credit card numbers are never stored - only opaque data/tokens

## Installation

1. Install the module via Apps menu or with command line:
   ```bash
   odoo-bin -i payment_authorize_add_card_via_customer_profile -d your_database
   ```

## Usage

### Adding a Card to a Customer

1. Navigate to a customer/partner form
2. Click the "Add Authorize.net Card" button in the form header
3. Enter card details (card number, expiration, CVV)
4. Click "Add Payment Method"
5. The card will be tokenized via Accept.js and saved as a payment token

### Viewing Payment Tokens

- View the count of payment tokens on the customer form
- Click the Payment Tokens smart button to view all stored tokens for the customer

## Technical Details

### Extended Models

#### AuthorizeAPI (`models/authorize_request.py`)
- Added `create_customer_profile_from_opaque_data()` method
- Calls Authorize.net `createCustomerProfileRequest` API
- Retrieves last 4 digits via `getCustomerPaymentProfileRequest`

#### ResPartner (`models/res_partner.py`)
- Added `payment_token_count` field (computed)
- Added `action_view_payment_tokens()` action for viewing tokens
- Added `action_add_authorize_card()` action for adding new cards

### Controllers

#### `/user/payment_method2/<provider_id>/<partner_id>`
- Renders the add card form
- Loads Authorize.net Accept.js library dynamically
- Validates provider and partner access

#### `/payment/authorize/profile` (POST)
- Receives opaque data from Accept.js tokenization
- Creates customer profile in Authorize.net
- Saves payment token in Odoo
- Returns success/failure status

### Frontend

#### `static/src/js/add_card_form.js`
- Integrates with Accept.js for client-side tokenization
- Handles form validation and submission
- Posts opaque data to backend controller

## API Flow

1. User navigates to add card form
2. Accept.js library is loaded (test or production based on provider state)
3. User enters card details
4. Accept.js tokenizes card data → opaque data (dataDescriptor + dataValue)
5. POST to `/payment/authorize/profile` with opaque data
6. Backend creates customer profile via Authorize.net API
7. Payment token is created in Odoo
8. User confirms success

## Security Considerations

- PCI-DSS compliant: Raw card data never reaches Odoo servers
- Access control: Users can only add cards to their own profiles
- Token-based: Only opaque data tokens are transmitted
- HTTPS required: Accept.js requires HTTPS communication

## Dependencies

- `payment_authorize` (Odoo 16.0 native module)

## Author

Trobz

## License

LGPL-3

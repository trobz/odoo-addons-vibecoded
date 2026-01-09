# Payment Authorize.net - Add Card via Customer Profile

This module extends the native `payment_authorize` module to add payment methods via Authorize.net Customer Profile without requiring a validation transaction (typically $0.01).

## Features

- **New endpoint**: `/user/payment_method2/` - Alternative payment method management page that adds cards without validation transactions
- **New endpoint**: `/payment/profile` - Creates Customer Profile from Accept.js opaque data
- **Extended AuthorizeAPI**: Added methods to create customer profiles and payment profiles directly from opaque data
- **No validation transaction required**: Payment methods are added by creating Customer Profiles in Authorize.net directly, avoiding the $0.01 validation charge

## Technical Details

The module is designed to be unintrusive and only extends the native `payment_authorize` module:

### Controllers

- `AuthorizeAddCardController` extends `AuthorizeController`
- New route `/user/payment_method2/<partner>` for the alternative payment method page
- New JSON route `/payment/profile` to process opaque data and create payment tokens

### Models

- Extends `AuthorizeAPI` with new methods:
  - `create_customer_profile_from_opaque_data()`: Creates customer and payment profiles from Accept.js opaque data
  - `_get_or_create_customer_profile()`: Gets or creates a customer profile based on partner ID

### Frontend

- Extends `payment.manage_form` JavaScript module
- Overrides payment processing for the new `/user/payment_method2/` page
- Dispatches opaque data to `/payment/profile` instead of creating a validation transaction

## Installation

1. Install this module via Odoo Apps menu
2. Ensure `payment_authorize` module is installed and configured
3. Access payment methods via the new `/user/payment_method2/<partner_id>` route

## Usage

1. Navigate to `/user/payment_method2/<partner_id>`
2. Fill in the payment details (card number, expiration, CVV)
3. Click "Save Payment Method"
4. The card is added via Authorize.net Customer Profile (no $0.01 charge)
5. The payment token is available for use in future transactions

## Comparison with payment_authorize_backend

| Feature | payment_authorize_backend | payment_authorize_add_card_via_customer_profile |
|----------|------------------------|--------------------------------------------|
| Validation Transaction | Yes ($0.01) | No |
| Implementation | Creates transaction first | Creates Customer Profile directly |
| Authorize.net API | createCustomerProfileFromTransaction | createCustomerProfile + createCustomerPaymentProfile |
| Endpoints | `/user/payment_method` | `/user/payment_method2` |

## License

LGPL-3

## Author

Vibecoded

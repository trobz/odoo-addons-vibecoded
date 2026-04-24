# Portal Content Only

Portal Content Only adds a `content_only` query parameter to frontend requests and makes portal/website pages render without header and footer when `content_only=True`.

## Features
- Auto-append `content_only=False` to all frontend URLs when the parameter is missing.
- Persist the `content_only` value in session so navigation keeps the same mode.
- Hide header and footer when `content_only=True` for both portal and regular frontend pages.

## Screenshots
- `content_only=False`, render page with header / footer: `image/page_with_header_footer_1.png`
- `content_only=True`, render page without header/footer: `image/page_without_header_footer.png`

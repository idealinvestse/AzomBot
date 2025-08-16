# AZOM Bot Embed (WordPress Plugin)

Embed the AZOM AI Agent chatbot on your WordPress site. Configure the backend URL, endpoint, default mode (Light/Full), and basic UI look & feel.

## Features
- Shortcode `[azom_bot]` to render the chat widget.
- Optional "Show on all pages" mode (no shortcode needed).
- Settings page under Settings → AZOM Bot.
- Calls your AZOM backend with `X-AZOM-Mode` header (Light/Full).
- Supports both Pipeline Server (`/chat/azom`) and Core API (`/api/v1/chat/azom`).

## Requirements
- WordPress 6.0+
- AZOM backend reachable from the site (local or hosted)

## Installation
1. Copy the folder `wordpress/azom-bot-plugin` into your WordPress plugins directory (`wp-content/plugins/`).
2. In wp-admin, go to Plugins and activate "AZOM Bot Embed".
3. Go to Settings → AZOM Bot and configure:
   - Backend Base URL (e.g., `http://localhost:8001` for Pipeline Server, or `http://localhost:8008` for Core API)
   - API Type (Pipeline Server or Core API)
   - Endpoint Path (`/chat/azom` or `/api/v1/chat/azom`)
   - Default Mode (`light` or `full`) → sets `X-AZOM-Mode`
   - Title, Welcome message, Position, Color, Button label
   - Show on all pages (optional)
4. Add the shortcode where you want the widget to appear:
   
   ```
   [azom_bot]
   ```

## CORS & Security
- Ensure your AZOM backend sends CORS headers allowing your WordPress origin (e.g., `Access-Control-Allow-Origin: https://your-site.com`).
- Rate limiting is recommended on the backend (the AZOM project includes `RateLimitingMiddleware`).
- If exposing the Core API externally, secure it (TLS, rate limiting, auth if needed).

## How it works
- The widget injects a floating chat panel with a toggle button.
- For Pipeline Server it POSTs `{ "message": "..." }` to `<BaseURL>/chat/azom`.
- For Core API it POSTs `{ "prompt": "..." }` to `<BaseURL>/api/v1/chat/azom`.
- The response is taken from `response` (preferred) or `message`.

## Troubleshooting
- 4xx/5xx responses: Check backend logs; verify endpoint and mode caps (Light: 8KB, Full: 32KB) documented in the AZOM repo.
- CORS errors in browser console: Configure backend CORS to allow the site origin and headers (especially `X-AZOM-Mode`).
- Mixed content errors: If your site runs over HTTPS, make sure the backend is also HTTPS or proxied.

## Uninstall
- Deactivating the plugin keeps your settings. To fully remove, delete the plugin folder and remove the `azom_bot_options` option from the database if needed.

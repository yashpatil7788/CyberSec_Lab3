# Stored XSS Demo — Web Server Security Assignment

## Overview
Demonstrates **Stored XSS (Variant 1)** for the Web Server Security assignment.

| Server | Port | Purpose |
|--------|------|---------|
| `app_vulnerable.py` | 5000 | ❌ Vulnerable — raw input rendered as HTML |
| `app_secure.py`     | 5001 | ✅ Secure — HTML-entity encoding on output |

## How to Run

```bash
# Install Flask if needed
pip install flask

# Run both servers at once (opens browser automatically)
python run_both.py

# Or run individually
python app_vulnerable.py   # http://127.0.0.1:5000
python app_secure.py       # http://127.0.0.1:5001
```

## Demo Payload (paste into the vulnerable app)
```html
<script>alert("XSS! Cookie: " + document.cookie)</script>
```

## What each file does

| File | Description |
|------|-------------|
| `app_vulnerable.py` | Flask app with Stored XSS flaw — uses `Markup()` to bypass escaping |
| `app_secure.py` | Flask app with fix — Jinja2 auto-escaping encodes all output |
| `templates/vulnerable.html` | UI for the vulnerable version (red theme) |
| `templates/secure.html` | UI for the secure version (green theme) |
| `run_both.py` | Starts both servers simultaneously |

## Assignment Details

- **Vulnerability category:** Cross-Site Scripting (XSS)
- **Variant implemented:** Stored XSS (Variant 1)
- **Mitigation implemented:** Context-aware output encoding via Jinja2 auto-escaping
- **Course:** Web Server Security — Dr. Soumyadev Maity

## Ownership Declaration

| Member name | Roll number | Category | Variant |
|---|---|---|---|
| Kamakshi Gupta | | Cross-Site Scripting (XSS) | Stored XSS (Variant 1) |

## Other XSS Mitigations (Theory)

| Mitigation | How it works |
|---|---|
| Framework auto-escaping | Jinja2/React escape by default — can't accidentally forget |
| HTML sanitiser (DOMPurify) | Strips dangerous tags when rich HTML must be accepted |
| Content Security Policy (CSP) | HTTP header blocking all inline scripts at browser level |
| HttpOnly cookies | Prevents JS from reading `document.cookie` |
| Safe DOM sinks | `textContent` instead of `innerHTML` — treats input as plain text |

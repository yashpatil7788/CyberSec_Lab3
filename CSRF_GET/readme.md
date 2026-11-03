# CSRF: GET-based forged action

Cyber Security (IT-30001), Autumn Semester 2026: Web Server Security assignment.
Group 16

| Member | Roll number | Category | Variant |
| Rahul Raut | IIt2024168 | CSRF | Variant 1: GET-based forged action |

**Stack:** Python, Flask (bank app) and a static attacker page served with `python -m http.server`.

| App | Local URL |
| --- | --- |
| Bank (vulnerable or fixed, one at a time) | http://localhost:5000 |
| Attacker site | http://localhost:8000 |

> Intentionally vulnerable demo. Run on `localhost` only and test only your own application.

## Project structure

```
csrf_get/
├── vulnerable/app.py          # flawed bank: state-changing GET /transfer
├── fixed/app.py               # mitigated bank: POST-only + anti-CSRF token
├── attacker/attack_get.html   # GET-based exploit page
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install flask
```

Demo users: `victim / victim123` (balance Rs. 10000) and `attacker / attacker123` (balance Rs. 0).
`http://localhost:5000/reset` resets balances and clears the session.

Use `localhost` for both the bank and the attacker page. Mixing `localhost` and `127.0.0.1` makes
the request cross-site, and the browser may then withhold the session cookie.

## Running the vulnerable app and the exploit

```bash
# Terminal 1: attacker site
cd attacker
python -m http.server 8000

# Terminal 2: vulnerable bank
cd vulnerable
python app.py
```

1. Open `http://localhost:5000/reset`, then log in at `http://localhost:5000/login` as `victim / victim123`.
   The dashboard shows Balance: Rs. 10000.
2. In a new tab open `http://localhost:8000/attack_get.html` (a harmless-looking "Cute cat pictures" page).
3. Return to the bank tab and refresh. The balance is Rs. 9500 and the history shows
   `victim -> attacker: Rs. 500`, though the victim never used the transfer form.

## (a) Vulnerable implementation

`vulnerable/app.py`, route `/transfer`:

```python
@app.route("/transfer")          # GET: state-changing action
def transfer():
    user = session.get("user")   # only check: is there a session cookie?
    to = request.args.get("to", "")
    amount = int(request.args.get("amount", "0"))
    ...
    USERS[user]["balance"] -= amount
    USERS[to]["balance"] += amount
```

The route changes account balances on a GET request and authenticates only with the session cookie.
There is no CSRF token and no proof of user intent.

## (b) Working exploit

`attacker/attack_get.html` contains a hidden 1x1 image whose source is the forged request:

```html
<img src="http://localhost:5000/transfer?to=attacker&amount=500" width="1" height="1" alt="">
```

When the victim, who is logged in to the bank, opens the attacker page, the browser loads the
image URL with a GET request to the bank and automatically attaches the victim's session cookie.
The server sees a valid session and transfers Rs. 500 to the attacker. (A hidden `<iframe>`
pointing at the same URL works equally well.)

## (c) Root cause

The server performs a state-changing action on a GET request and authenticates it only with a
cookie, which the browser sends automatically with every request to that site, including requests
started by another site's page. The server has no proof that the user intended the action.

## (d) Mitigation implemented: anti-CSRF (synchronizer) token

`fixed/app.py` changes:

1. `/transfer` accepts `POST` only, so a forged GET gets `405 Method Not Allowed`.
2. At login the server generates a random token (`secrets.token_hex(32)`) and stores it in the session.
3. The real transfer form includes the token as a hidden field. The server checks it with
   `hmac.compare_digest` and returns `403` if it is missing or wrong.
4. Sessions without a token (for example, a stale cookie left from the vulnerable app) are cleared
   and the user is sent to the login page.

```python
@app.route("/transfer", methods=["POST"])
def transfer():
    ...
    sent = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not expected or not hmac.compare_digest(sent, expected):
        abort(403, description="CSRF token missing or invalid - request blocked.")
```

The attacker's page can send requests to the bank but cannot read the bank's pages (same-origin
policy), so it cannot learn the token.

### Running the fixed app

Stop the vulnerable app (Ctrl+C), since both use port 5000, then:

```bash
cd fixed
python app.py
```

1. Open `http://localhost:5000/logout`, then log in again as `victim / victim123`.
2. Open `http://localhost:8000/attack_get.html` again (the same payload).
3. Refresh the dashboard. The balance stays Rs. 10000. In the browser DevTools Network tab
   (open on the attacker tab) the forged request `transfer?to=attacker&amount=500` returns
   `405 METHOD NOT ALLOWED` with `Allow: OPTIONS, POST`.
4. A legitimate transfer from the dashboard form still works.

Screenshot of the blocked attempt: `screenshots/blocked_405.png` (add before submission).

## (e) Other mitigations (theory)

- **SameSite cookies.** Setting the session cookie to `SameSite=Lax` or `Strict` makes the browser
  withhold it on cross-site requests, so a forged request reaches the server unauthenticated. Lax
  still sends cookies on top-level GET navigations, which is another reason not to change state on
  GET, so it works best together with tokens.
- **Re-authentication for sensitive actions.** Asking for the password, an OTP or a confirmation
  before a high-risk action works because the attacker cannot supply a secret they do not know,
  even if the forged request carries the session cookie.
- **Avoiding state-changing GET requests.** GET is meant to be safe and idempotent. It can be
  triggered by images, links, prefetching and crawlers without any user action, so moving actions
  to POST, PUT or DELETE removes the easiest attack vector. It is not enough alone, because an
  auto-submitting cross-site POST form still works without a token.
- **Anti-CSRF (synchronizer) tokens** (implemented above): the server accepts a state-changing
  request only if it carries an unpredictable value tied to the user's session, which only pages
  served by the real site can contain.

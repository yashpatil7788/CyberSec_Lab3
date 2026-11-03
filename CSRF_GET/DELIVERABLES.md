# CSRF - Variant 1: GET-based forged action

Cyber Security (IT-30001), Web Server Security assignment.

## How to run

```bash
pip install flask

# Terminal 1 - vulnerable app (stop it before starting the fixed one; both use port 5000)
cd vulnerable && python app.py

# Terminal 2 - attacker site on a different port (same host name "localhost")
cd attacker && python -m http.server 8000
```

Demo users: `victim / victim123` (Rs. 10000) and `attacker / attacker123` (Rs. 0).
Use `http://localhost:5000/reset` to reset state between takes.

Use the host name `localhost` for both the app and the attacker page. Cookies are
not port-specific, so the browser sends the victim's session cookie. Mixing
`localhost` and `127.0.0.1` makes the request cross-site, and the browser's default
SameSite=Lax handling may then block the cookie and hide the attack.

## (a) Vulnerable implementation

File: `vulnerable/app.py`, route `/transfer` (the block commented
"VULNERABLE CODE PATH"):

```python
@app.route("/transfer")          # GET: state-changing action
def transfer():
    user = session.get("user")   # only check: is there a session cookie?
    to = request.args.get("to")
    amount = int(request.args.get("amount"))
    ...
    USERS[user]["balance"] -= amount
    USERS[to]["balance"] += amount
```

## (b) Working exploit

Attacker page `attacker/attack_get.html` contains:

```html
<img src="http://localhost:5000/transfer?to=attacker&amount=500" width="1" height="1">
```

Steps for the video:
1. Open `http://localhost:5000/login` and log in as `victim`. Note balance Rs. 10000.
2. In a new tab open `http://localhost:8000/attack_get.html` (looks like a cat-picture page).
3. Go back to the bank tab and refresh the dashboard. The balance is Rs. 9500 and the history
   shows `victim -> attacker: Rs. 500`, though the victim never clicked anything in the bank.
4. (Optional) Log in as `attacker` in a private window to show Rs. 500 received.

## (c) Root cause

The server performs a state-changing action on a GET request and authenticates it
only with the session cookie, which the browser attaches automatically to every
request to that site, including ones triggered from another site's page (`<img>`,
iframe, link). The server has no proof that the user intended the action.

## (d) Mitigation implemented: anti-CSRF (synchronizer) token

File: `fixed/app.py`. Changes:
1. `/transfer` accepts `POST` only, so the forged GET gets `405 Method Not Allowed`.
2. On login a random token is generated (`secrets.token_hex(32)`) and stored in the session.
3. The real transfer form contains it as a hidden field, and the server verifies it with
   `hmac.compare_digest`; if it is missing or wrong, the server returns `403`.

Why the attacker cannot get past it: the token is secret and per-session. The attacker's
page can send requests to the bank but, because of the same-origin policy, cannot read the
bank's pages to learn the token.

Evidence for the video:
1. Stop the vulnerable app, run `cd fixed && python app.py`, log in as `victim`.
2. Open `http://localhost:8000/attack_get.html` again (same payload).
3. Balance is unchanged. Optionally open the browser DevTools Network tab to show the
   forged request returned `405`. Also show `http://localhost:8000/attack_post.html`
   returning `403 CSRF token missing or invalid`.
4. Make a legitimate transfer from the dashboard form to show it still works.

Screenshots to capture: balance before the attack, balance after (vulnerable), blocked
request (405 or 403 in DevTools), balance unchanged (fixed), working legitimate transfer.

## (e) Other mitigations (theory)

- **SameSite cookies.** Setting the session cookie with `SameSite=Lax` or `Strict` makes
  the browser withhold it on cross-site requests, so a forged request from the attacker's
  page arrives unauthenticated. Lax still sends cookies on top-level GET navigations, which
  is one more reason not to change state on GET. Browser support and same-site subdomain
  cases mean it is best used with tokens as defence in depth.
- **Re-authentication for sensitive actions.** Asking for the password, an OTP or a
  confirmation before a high-risk action (money transfer, password change) works because
  the attacker cannot supply a secret they do not know, even if a forged request carries
  the session cookie.
- **Avoiding state-changing GET requests.** GET is meant to be safe and idempotent. GET
  requests can be triggered by `<img>` tags, links, prefetching and crawlers without any
  user action, so moving actions to POST/PUT/DELETE removes the easiest attack vector. It is
  not enough alone, because an auto-submitting cross-site POST form still works without a token.
- **Anti-CSRF (synchronizer) tokens** (the one implemented): the server accepts a request only
  if it carries an unpredictable value tied to the user's session, which only pages
  served by the real site can contain.

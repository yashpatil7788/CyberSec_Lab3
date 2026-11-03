"""
CSRF through a state-changing GET request.
"""
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "demo-secret-key-not-for-production"

USERS = {}
HISTORY = []


def reset_state():
    USERS.clear()
    USERS.update({
        "victim":   {"password": "victim123",   "balance": 10000},
        "attacker": {"password": "attacker123", "balance": 0},
    })
    HISTORY.clear()


reset_state()

STYLE = """
<style>
 body{font-family:Arial,sans-serif;max-width:560px;margin:40px auto;padding:0 16px}
 .card{border:1px solid #ccc;border-radius:8px;padding:16px;margin:12px 0}
 input{padding:6px;margin:4px 0;width:95%}
 button{padding:8px 14px;cursor:pointer}
 .err{color:#b00020}
 .tag{background:#b00020;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px}
</style>
"""

LOGIN_HTML = STYLE + """
<h2>Demo Bank <span class="tag">VULNERABLE</span></h2>
<div class="card">
  <form method="POST" action="{{ url_for('login') }}">
    <label>Username</label><br><input name="username" required><br>
    <label>Password</label><br><input name="password" type="password" required><br>
    <button type="submit">Login</button>
  </form>
  {% if error %}<p class="err">{{ error }}</p>{% endif %}
  <p><small>Demo users: victim / victim123 &nbsp;|&nbsp; attacker / attacker123</small></p>
</div>
"""

DASH_HTML = STYLE + """
<h2>Demo Bank <span class="tag">VULNERABLE</span></h2>
<p>Logged in as <b>{{ user }}</b> | <a href="{{ url_for('logout') }}">Logout</a></p>
<div class="card"><h3>Balance: Rs. {{ balance }}</h3></div>

<div class="card">
  <h3>Transfer money</h3>
  <!-- The legitimate form itself uses GET: this is the design flaw. -->
  <form method="GET" action="{{ url_for('transfer') }}">
    <label>To (username)</label><br><input name="to" required><br>
    <label>Amount</label><br><input name="amount" type="number" min="1" required><br>
    <button type="submit">Send</button>
  </form>
</div>

<div class="card">
  <h3>Transaction history</h3>
  {% if history %}<ul>{% for h in history %}<li>{{ h }}</li>{% endfor %}</ul>
  {% else %}<p>No transactions yet.</p>{% endif %}
</div>
"""


@app.route("/")
def index():
    return redirect(url_for("dashboard" if "user" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u in USERS and USERS[u]["password"] == p:
            session["user"] = u
            return redirect(url_for("dashboard"))
        error = "Invalid credentials"
    return render_template_string(LOGIN_HTML, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    mine = [h for h in HISTORY if user in h]
    return render_template_string(DASH_HTML, user=user,
                                  balance=USERS[user]["balance"], history=mine)


# ---------------------------------------------------------------------------
# VULNERABLE CODE PATH (item a)
# State-changing action exposed on GET. The only check is "is there a valid
# session cookie?". The browser attaches that cookie automatically to ANY
# request to this site, including ones triggered by <img src=...> on another
# page. There is no CSRF token and no proof the user intended the action.
# ---------------------------------------------------------------------------
@app.route("/transfer")
def transfer():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    to = request.args.get("to", "")
    try:
        amount = int(request.args.get("amount", "0"))
    except ValueError:
        return "Invalid amount", 400

    if to not in USERS or to == user or amount <= 0 or amount > USERS[user]["balance"]:
        return "Transfer failed", 400

    USERS[user]["balance"] -= amount
    USERS[to]["balance"] += amount
    HISTORY.append(f"{user} -> {to}: Rs. {amount}")
    return redirect(url_for("dashboard"))


# Demo helper: resets balances between takes while recording the video.
@app.route("/reset")
def reset():
    reset_state()
    session.clear()
    return "State reset. <a href='/login'>Login</a>"


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=False)

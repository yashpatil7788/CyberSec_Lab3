"""
SECURE Flask App — Stored XSS Mitigation Demo
Run: python app_secure.py
URL: http://127.0.0.1:5001
"""
import sqlite3
from flask import Flask, request, redirect, url_for, g, render_template

app = Flask(__name__)
DB = "secure.db"

# ── database helpers ───────────────────────────────────────────────────────────
def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(_):
    db = getattr(g, "_db", None)
    if db: db.close()

def init_db():
    with app.app_context():
        get_db().execute(
            "CREATE TABLE IF NOT EXISTS comments"
            "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " author TEXT NOT NULL, body TEXT NOT NULL)"
        )
        get_db().commit()

# ── routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    rows = get_db().execute("SELECT * FROM comments ORDER BY id DESC").fetchall()
    # ✅ SECURE: we pass plain Python strings — Jinja2 auto-escaping converts
    #    < > " ' & to &lt; &gt; &#34; &#39; &amp; before they hit the HTML.
    #    No Markup() wrapper → no raw injection possible.
    comments = [{"author": r["author"], "body": r["body"]} for r in rows]
    return render_template("secure.html", comments=comments)

@app.route("/post", methods=["POST"])
def post():
    author = request.form.get("author", "").strip()
    body   = request.form.get("body",   "").strip()
    if author and body:
        # Store raw (encoding happens at render time, not storage time)
        get_db().execute("INSERT INTO comments(author,body) VALUES(?,?)", (author, body))
        get_db().commit()
    return redirect(url_for("index"))

@app.route("/clear")
def clear():
    get_db().execute("DELETE FROM comments")
    get_db().commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    print("\n  ✅  SECURE app  →  http://127.0.0.1:5001\n")
    app.run(port=5001, debug=False)

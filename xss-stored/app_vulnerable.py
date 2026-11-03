"""
VULNERABLE Flask App — Stored XSS Demo
Run: python app_vulnerable.py
URL: http://127.0.0.1:5000
"""
import sqlite3
from flask import Flask, request, redirect, url_for, g, render_template
from markupsafe import Markup

app = Flask(__name__)
DB = "vuln.db"

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
    # ❌ VULNERABLE: we wrap each field in Markup() which disables HTML escaping.
    #    Whatever HTML/JS was stored in the DB is injected raw into the page.
    comments = [
        {"author": Markup(r["author"]), "body": Markup(r["body"])}
        for r in rows
    ]
    return render_template("vulnerable.html", comments=comments)

@app.route("/post", methods=["POST"])
def post():
    author = request.form.get("author", "").strip()
    body   = request.form.get("body",   "").strip()
    if author and body:
        # ❌ VULNERABLE: raw, unvalidated input stored directly
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
    print("\n  ❌  VULNERABLE app  →  http://127.0.0.1:5000\n")
    app.run(port=5000, debug=False)

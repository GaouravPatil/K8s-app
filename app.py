from flask import Flask, request, jsonify, render_template_string
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def require_env(name: str) -> str:
    """Read env var at runtime. Fail fast if missing (production-safe)."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def get_conn():
    # Read ENV on every call — no global dict, no hardcoded defaults.
    # Changing ENV at runtime takes effect on next request without code change.
    return psycopg.connect(
        host=require_env("DB_HOST"),
        port=require_env("DB_PORT"),
        dbname=require_env("DB_NAME"),
        user=require_env("DB_USER"),
        password=require_env("DB_PASSWORD"),
    )


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()

# ---------- HTML page: email form + display on same screen ----------
PAGE = """
<!doctype html>
<html><body style="font-family:sans-serif; max-width:500px; margin:40px auto;">
  <h2>Email storage demo</h2>
  <form method="POST" action="/">
    <input type="email" name="email" placeholder="type email here" required
           value="{{ typed or '' }}" style="padding:8px; width:70%;">
    <button type="submit" style="padding:8px;">Save</button>
  </form>
  {% if typed %}
    <p><b>You typed:</b> {{ typed }}</p>
  {% endif %}
  {% if msg %}<p>{{ msg }}</p>{% endif %}
  <h3>Saved emails (from Postgres):</h3>
  <ul>{% for u in users %}<li>{{ u[1] }}</li>{% else %}<li>No emails yet</li>{% endfor %}</ul>
</body></html>
"""

def fetch_users():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, created_at FROM users ORDER BY id DESC;")
            return cur.fetchall()

# 1. Form UI on root: shows email field, saves to DB, displays typed email on same screen
@app.get("/")
def home():
    return render_template_string(PAGE, users=fetch_users(), typed=None, msg=None)

@app.get("/exit")
def exit():
    return "Exit!"
    

@app.post("/")
def home_save():
    email = request.form.get("email", "").strip()
    msg, typed = None, email
    if email:
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO users (email) VALUES (%s);", (email,))
                conn.commit()
            msg = "Saved to Postgres."
        except psycopg.errors.UniqueViolation:
            msg = "This email already exists."
    return render_template_string(PAGE, users=fetch_users(), typed=typed, msg=msg)

@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

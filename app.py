import os
import re
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from card_crypto import CardCipher, CardError, mask_pan, new_token, normalize_pan
from rate_limit import RateLimiter
from storage import CardStore


TOKEN_PATTERN = re.compile(r"^tok_[a-f0-9]{32}$")
app = Flask(__name__, instance_relative_config=True)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
instance = Path(app.instance_path)
instance.mkdir(parents=True, exist_ok=True)

key_path = instance / "secret.key"
if not key_path.exists():
    key_path.write_bytes(os.urandom(32))
try:
    os.chmod(key_path, 0o600)
except OSError:
    pass

cipher = CardCipher(key_path.read_bytes())
store = CardStore(instance / "vault.db")
limiter = RateLimiter()


def rate_limited():
    return not limiter.allow(request.remote_addr or "unknown")


@app.after_request
def headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "connect-src 'self'; frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/cards")
def cards():
    return jsonify(cards=[dict(row) for row in store.list_masked()])


@app.post("/api/tokenize")
def tokenize():
    if rate_limited():
        return jsonify(error="Too many requests. Wait one minute."), 429
    try:
        body = request.get_json(silent=True) or {}
        pan = normalize_pan(body.get("pan"))
        token = new_token()
        masked = mask_pan(pan)
        encrypted = cipher.encrypt(pan, token)
        store.save(token, encrypted, masked)
        return jsonify(token=token, masked_pan=masked)
    except CardError as exc:
        return jsonify(error=str(exc)), 400


@app.post("/api/reveal")
def reveal():
    if rate_limited():
        return jsonify(error="Too many requests. Wait one minute."), 429
    body = request.get_json(silent=True) or {}
    token = (body.get("token") or "").strip()
    if not TOKEN_PATTERN.fullmatch(token):
        return jsonify(error="Invalid token format."), 400
    row = store.get(token)
    if row is None:
        return jsonify(error="Token not found."), 404
    try:
        pan = cipher.decrypt(row["encrypted_pan"], token)
        return jsonify(pan=pan, masked_pan=row["masked_pan"])
    except Exception:
        return jsonify(error="Stored ciphertext failed authentication."), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

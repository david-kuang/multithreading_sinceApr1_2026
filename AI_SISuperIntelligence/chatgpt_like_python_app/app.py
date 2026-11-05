"""
A compact, single-user ChatGPT-like web application.

Features
--------
- Flask web UI with conversation history.
- OpenAI Responses API integration.
- SQLite persistence through SQLAlchemy.
- Server-side API key configuration (never sent to the browser).
- CSRF protection, secure cookie settings, request size limits.
- Basic per-IP rate limiting for chat requests.
- Server-side validation and graceful API/database error handling.

Run locally:
    python -m venv .venv
    # Windows: .venv\Scripts\activate
    # macOS/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    set OPENAI_API_KEY=your_key       # Windows CMD
    # export OPENAI_API_KEY=your_key  # macOS/Linux
    python app.py

This is a single-user starter suitable for private deployment behind HTTPS.
For multi-user public production, add user authentication, a reverse proxy,
centralized rate limiting, monitoring, backups, and a managed database.
"""

from __future__ import annotations

import logging
import os
import secrets
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Any

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_MESSAGE_CHARS = int(os.getenv("MAX_MESSAGE_CHARS", "12000"))
MAX_REQUEST_BYTES = int(os.getenv("MAX_REQUEST_BYTES", "20000"))
RATE_LIMIT_COUNT = int(os.getenv("RATE_LIMIT_COUNT", "20"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(BASE_DIR, "chat_history.db").replace("\\", "/"),
)

db = SQLAlchemy()


class Conversation(db.Model):
    """A named conversation belonging to this single-user installation."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, default="New chat")
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    messages = db.relationship(
        "Message", backref="conversation", lazy=True,
        cascade="all, delete-orphan", order_by="Message.id"
    )


class Message(db.Model):
    """One user or assistant message stored in a conversation."""

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure the Flask application; initialize database and routes."""

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32),
        SQLALCHEMY_DATABASE_URI=DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=MAX_REQUEST_BYTES,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "0") == "1",
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("chat_app")

    def get_openai_client() -> OpenAI:
        """Build an OpenAI client from the server-side environment variable."""
        key = app.config.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Set it in the server environment."
            )
        return OpenAI(api_key=key, timeout=45.0, max_retries=2)

    def csrf_token() -> str:
        """Return a session-bound CSRF token, creating one when necessary."""
        token = session.get("_csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return token

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def protect_state_changes() -> None:
        """Reject state-changing form/JSON requests without a valid CSRF token."""
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
            expected = session.get("_csrf_token")
            if not supplied or not expected or not secrets.compare_digest(supplied, expected):
                abort(400, description="Invalid or missing CSRF token.")

    # Simple in-process limiter: adequate for a single-process private app.
    # Use Redis or a gateway limiter when running multiple workers/instances.
    request_log: dict[str, list[float]] = {}

    def rate_limit(view):
        """Limit a route by remote address using a rolling in-memory time window."""
        @wraps(view)
        def wrapped(*args, **kwargs):
            now = time.monotonic()
            ip = request.remote_addr or "unknown"
            recent = [t for t in request_log.get(ip, []) if now - t < RATE_LIMIT_WINDOW]
            if len(recent) >= RATE_LIMIT_COUNT:
                return jsonify(error="Too many requests. Please wait and try again."), 429
            recent.append(now)
            request_log[ip] = recent
            return view(*args, **kwargs)
        return wrapped

    @app.get("/")
    def index():
        """Render the chat interface and the conversation sidebar."""
        conversations = Conversation.query.order_by(Conversation.updated_at.desc()).all()
        active_id = request.args.get("conversation_id", type=int)
        active = db.session.get(Conversation, active_id) if active_id else None
        if active is None and conversations:
            active = conversations[0]
        return render_template_string(
            PAGE,
            conversations=conversations,
            active=active,
            model=DEFAULT_MODEL,
        )

    @app.post("/conversations")
    def new_conversation():
        """Create an empty conversation and redirect to it."""
        conversation = Conversation(title="New chat")
        db.session.add(conversation)
        db.session.commit()
        return redirect(url_for("index", conversation_id=conversation.id))

    @app.post("/conversations/<int:conversation_id>/delete")
    def delete_conversation(conversation_id: int):
        """Delete a conversation and all its messages."""
        conversation = db.session.get(Conversation, conversation_id)
        if conversation is None:
            abort(404)
        db.session.delete(conversation)
        db.session.commit()
        flash("Conversation deleted.", "success")
        return redirect(url_for("index"))

    @app.post("/api/chat")
    @rate_limit
    def chat():
        """Persist a user prompt, call the model, persist its reply, and return JSON."""
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Request body must be JSON."), 400

        prompt = payload.get("message")
        conversation_id = payload.get("conversation_id")
        if not isinstance(prompt, str) or not prompt.strip():
            return jsonify(error="Message cannot be empty."), 400
        prompt = prompt.strip()
        if len(prompt) > MAX_MESSAGE_CHARS:
            return jsonify(error=f"Message exceeds {MAX_MESSAGE_CHARS} characters."), 413

        conversation = None
        if conversation_id is not None:
            if not isinstance(conversation_id, int):
                return jsonify(error="Invalid conversation ID."), 400
            conversation = db.session.get(Conversation, conversation_id)
            if conversation is None:
                return jsonify(error="Conversation not found."), 404
        else:
            conversation = Conversation(title=prompt[:60])
            db.session.add(conversation)
            db.session.flush()

        # Limit prompt history to avoid unbounded context growth.
        history = [
            {"role": m.role, "content": m.content}
            for m in conversation.messages[-20:]
            if m.role in {"user", "assistant"}
        ]
        user_message = Message(
            conversation_id=conversation.id, role="user", content=prompt
        )
        db.session.add(user_message)
        db.session.commit()

        try:
            client = get_openai_client()
            # Responses API accepts a sequence of role/content input messages.
            response = client.responses.create(
                model=DEFAULT_MODEL,
                input=history + [{"role": "user", "content": prompt}],
            )
            answer = (response.output_text or "").strip()
            if not answer:
                logger.warning("Model returned an empty response.")
                return jsonify(
                    error="The model returned an empty response. Please try again.",
                    conversation_id=conversation.id,
                ), 502

            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
            )
            conversation.updated_at = datetime.now(timezone.utc)
            db.session.add(assistant_message)
            db.session.commit()

            return jsonify(
                answer=answer,
                conversation_id=conversation.id,
                message_id=assistant_message.id,
            )

        except RuntimeError as exc:
            db.session.rollback()
            logger.error("Configuration error: %s", exc)
            return jsonify(error=str(exc)), 503
        except RateLimitError:
            db.session.rollback()
            logger.warning("OpenAI rate limit reached.")
            return jsonify(error="AI provider rate limit reached. Try again shortly."), 429
        except APITimeoutError:
            db.session.rollback()
            logger.exception("OpenAI request timed out.")
            return jsonify(error="The AI request timed out. Please try again."), 504
        except APIConnectionError:
            db.session.rollback()
            logger.exception("Could not connect to OpenAI.")
            return jsonify(error="Could not connect to the AI provider. Check network access."), 502
        except APIStatusError as exc:
            db.session.rollback()
            logger.exception("OpenAI API returned status %s.", exc.status_code)
            return jsonify(
                error=f"AI provider returned an error (HTTP {exc.status_code})."
            ), 502
        except Exception:
            db.session.rollback()
            logger.exception("Unexpected chat endpoint failure.")
            return jsonify(error="Unexpected server error. Check server logs."), 500

    @app.get("/api/conversations/<int:conversation_id>")
    def get_conversation(conversation_id: int):
        """Return all messages for a conversation as JSON."""
        conversation = db.session.get(Conversation, conversation_id)
        if conversation is None:
            return jsonify(error="Conversation not found."), 404
        return jsonify(
            id=conversation.id,
            title=conversation.title,
            messages=[
                {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
                for m in conversation.messages
            ],
        )

    @app.errorhandler(400)
    def bad_request(error):
        """Return readable JSON errors for API calls and HTML errors otherwise."""
        if request.path.startswith("/api/"):
            return jsonify(error=getattr(error, "description", "Bad request.")), 400
        return getattr(error, "description", "Bad request."), 400

    @app.errorhandler(404)
    def not_found(error):
        """Render a simple not-found response."""
        if request.path.startswith("/api/"):
            return jsonify(error="Not found."), 404
        return "Not found.", 404

    @app.errorhandler(413)
    def too_large(error):
        """Explain when an incoming request exceeds the configured size limit."""
        return jsonify(error="Request is too large."), 413

    with app.app_context():
        db.create_all()

    return app


PAGE = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Chat</title>
<style>
:root { color-scheme: dark; --bg:#212121; --panel:#171717; --muted:#a1a1aa; --line:#3a3a3a; --accent:#10a37f; }
* { box-sizing:border-box; }
body { margin:0; font:15px/1.5 system-ui, sans-serif; background:var(--bg); color:#eee; }
.layout { display:grid; grid-template-columns:260px 1fr; min-height:100vh; }
aside { background:var(--panel); padding:16px; border-right:1px solid var(--line); }
.brand { font-weight:700; font-size:18px; margin:4px 0 18px; }
button, .button { cursor:pointer; border:1px solid var(--line); color:#eee; background:#292929; border-radius:9px; padding:10px 13px; }
button:hover, .button:hover { background:#383838; }
.new { width:100%; margin-bottom:16px; }
.chat-link { display:block; color:#ddd; text-decoration:none; padding:9px; border-radius:8px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.chat-link.active, .chat-link:hover { background:#303030; }
main { display:flex; flex-direction:column; min-width:0; height:100vh; }
header { padding:14px 22px; border-bottom:1px solid var(--line); color:var(--muted); }
#messages { flex:1; overflow:auto; padding:24px max(20px, calc((100% - 850px)/2)); }
.message { white-space:pre-wrap; overflow-wrap:anywhere; padding:17px 19px; margin:12px 0; border-radius:12px; }
.user { background:#303030; margin-left:10%; }
.assistant { background:#262626; margin-right:10%; }
.role { color:var(--accent); font-size:12px; text-transform:uppercase; font-weight:700; margin-bottom:5px; }
.composer { width:min(850px, calc(100% - 32px)); margin:12px auto 24px; }
form#chat-form { display:flex; gap:8px; background:#303030; border:1px solid #555; border-radius:14px; padding:8px; }
textarea { flex:1; resize:vertical; min-height:48px; max-height:180px; background:transparent; border:0; outline:0; color:white; font:inherit; padding:10px; }
#send { background:var(--accent); border:0; font-weight:700; }
#status { min-height:22px; color:var(--muted); padding:4px 8px; }
.delete { margin:12px 0; width:100%; }
.flash { color:#fca5a5; }
@media(max-width:700px) { .layout { grid-template-columns:1fr; } aside { display:none; } main { height:100vh; } }
</style>
</head>
<body>
<div class="layout">
<aside>
  <div class="brand">AI Chat</div>
  <form method="post" action="{{ url_for('new_conversation') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button class="new" type="submit">＋ New chat</button>
  </form>
  {% for item in conversations %}
    <a class="chat-link {{ 'active' if active and active.id == item.id else '' }}"
       href="{{ url_for('index', conversation_id=item.id) }}">{{ item.title }}</a>
  {% endfor %}
  {% if active %}
  <form method="post" action="{{ url_for('delete_conversation', conversation_id=active.id) }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button class="delete" type="submit">Delete current chat</button>
  </form>
  {% endif %}
</aside>
<main>
<header>Model: {{ model }} · Conversation history is stored locally in SQLite</header>
<section id="messages" aria-live="polite">
  {% if active %}
    {% for message in active.messages %}
      <div class="message {{ message.role }}"><div class="role">{{ message.role }}</div>{{ message.content }}</div>
    {% endfor %}
  {% else %}
    <div style="text-align:center;color:#aaa;margin-top:18vh">
      <h1>How can I help?</h1><p>Ask a question to start a conversation.</p>
    </div>
  {% endif %}
</section>
<div class="composer">
  <div id="status" role="status"></div>
  <form id="chat-form">
    <textarea id="message" placeholder="Message AI Chat..." aria-label="Message" required></textarea>
    <button id="send" type="submit">Send</button>
  </form>
</div>
</main>
</div>
<script>
const csrfToken = {{ csrf_token()|tojson }};
let conversationId = {{ (active.id if active else none)|tojson }};
const messages = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const statusBox = document.getElementById("status");
const send = document.getElementById("send");

function addMessage(role, content) {
  const wrapper = document.createElement("div");
  wrapper.className = "message " + role;
  const label = document.createElement("div");
  label.className = "role";
  label.textContent = role;
  const body = document.createElement("div");
  body.textContent = content;
  wrapper.append(label, body);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || send.disabled) return;
  addMessage("user", message);
  input.value = "";
  send.disabled = true;
  statusBox.textContent = "Thinking…";
  try {
    const response = await fetch("{{ url_for('chat') }}", {
      method: "POST",
      headers: {"Content-Type":"application/json", "X-CSRF-Token":csrfToken},
      body: JSON.stringify({message, conversation_id:conversationId})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Request failed.");
    conversationId = data.conversation_id;
    addMessage("assistant", data.answer);
    statusBox.textContent = "";
    if (window.location.search !== "?conversation_id=" + conversationId) {
      history.replaceState({}, "", "/?conversation_id=" + conversationId);
    }
  } catch (error) {
    statusBox.textContent = error.message;
  } finally {
    send.disabled = false;
    input.focus();
  }
});
messages.scrollTop = messages.scrollHeight;
</script>
</body>
</html>
"""


app = create_app()

if __name__ == "__main__":
    # Debug mode is deliberately disabled by default.
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )

# Python AI Chat Web App

A compact single-user ChatGPT-like web application built with Flask, SQLite,
SQLAlchemy, and the official OpenAI Python SDK.

## Files

```text
chatgpt_like_python_app/
├── app.py
├── requirements.txt
├── README.md
└── tests/
    └── test_app.py
```

## Requirements

- Python 3.10+
- An OpenAI API key
- Internet access to the OpenAI API

## Install on Windows CMD

```bat
cd chatgpt_like_python_app
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
set OPENAI_API_KEY=YOUR_OPENAI_API_KEY
set FLASK_SECRET_KEY=replace-with-a-long-random-secret
python app.py
```

Open http://127.0.0.1:5000

The environment variables set with `set` apply only to the current CMD window.
For a persistent setup, configure them in your operating-system or deployment
environment. Never commit API keys to source control.

## Run tests

```bat
python -m pytest -v
```

## Database schema

`Conversation`
- `id`: integer primary key
- `title`: short conversation title
- `created_at`: UTC timestamp
- `updated_at`: UTC timestamp

`Message`
- `id`: integer primary key
- `conversation_id`: foreign key to Conversation
- `role`: `user` or `assistant`
- `content`: message text
- `created_at`: UTC timestamp

The SQLite database is created automatically as `chat_history.db`.

## Configuration

| Environment variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | none | Required API key |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Model identifier |
| `FLASK_SECRET_KEY` | random per process | Session signing key; set a stable secret |
| `DATABASE_URL` | local SQLite | SQLAlchemy database URL |
| `HOST` | `127.0.0.1` | Bind address |
| `PORT` | `5000` | HTTP port |
| `COOKIE_SECURE` | `0` | Set to `1` behind HTTPS |
| `MAX_MESSAGE_CHARS` | `12000` | Prompt length limit |
| `RATE_LIMIT_COUNT` | `20` | Requests per IP in the window |
| `RATE_LIMIT_WINDOW` | `60` | Rate-limit window in seconds |

## Function guide

- `create_app(test_config=None)`: application factory; configures Flask,
  SQLAlchemy, security checks, routes, error handlers, and schema creation.
- `get_openai_client()`: constructs the server-side OpenAI SDK client.
- `csrf_token()`: creates or returns the CSRF token stored in the session.
- `protect_state_changes()`: checks CSRF tokens for POST/PUT/PATCH/DELETE.
- `rate_limit(view)`: decorator implementing a simple in-memory per-IP limiter.
- `index()`: renders conversation list and selected chat.
- `new_conversation()`: creates a conversation.
- `delete_conversation(id)`: deletes a conversation and its messages.
- `chat()`: validates prompt, stores it, calls the Responses API, stores the
  assistant response, and returns JSON.
- `get_conversation(id)`: returns a conversation and its messages as JSON.
- `bad_request(error)`: formats HTTP 400 errors.
- `not_found(error)`: formats HTTP 404 errors.
- `too_large(error)`: formats HTTP 413 errors.
- `main` block: starts the local Flask development server.

## Deployment and security notes

This is a complete runnable single-user starter, not a fully hardened
multi-tenant SaaS deployment. Before exposing it publicly:

1. Add real user authentication and authorization; current conversations are
   shared by anyone who can reach this instance.
2. Use HTTPS and set `COOKIE_SECURE=1`.
3. Set a persistent, randomly generated `FLASK_SECRET_KEY`.
4. Replace the in-memory rate limiter with Redis or a gateway limiter when
   running multiple workers.
5. Use PostgreSQL for concurrent production workloads and run managed schema
   migrations (for example, Flask-Migrate/Alembic).
6. Add backups, log retention, monitoring, and a privacy/data-retention policy.
7. Run behind a production WSGI server such as Waitress (Windows) or Gunicorn
   (Linux); do not use Flask's development server for public production.
8. Review provider data handling, costs, and applicable privacy requirements.

The application does not expose the API key to browser JavaScript. Messages
and conversation history are stored in the local database.

# Practice Tracker

A full-stack web app: users register/log in and track their guitar (or any
instrument) practice sessions, with stats on total time practiced per song/skill.

**Verified working** — the full flow below (register → login → create sessions →
fetch stats → auth rejection on bad token/password) was tested end-to-end.

## Stack

- **Backend:** Python, Flask, SQLAlchemy (ORM), SQLite (database), PyJWT (auth)
- **Frontend:** Plain HTML/CSS/JS

## What this demonstrates

- **REST API design** — proper HTTP methods (GET/POST/PUT/DELETE) and status codes (200/201/400/401/404/409)
- **Authentication** — password hashing (never stored in plain text), JWT-based stateless auth, protected routes via a decorator
- **Database design** — a one-to-many relationship (User → PracticeSessions) with a foreign key, cascading deletes
- **Authorization vs. authentication** — every session route checks that the session belongs to the requesting user, not just that *some* valid user is logged in
- **Security practices**: vague login error messages to prevent username enumeration, 404-not-403 on other users' resources to avoid leaking existence

## How to run it

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

This starts the API at `http://127.0.0.1:5001`. It auto-creates `practice_tracker.db` (a SQLite file) on first run — no separate database install needed.

### 2. Frontend

Just open `frontend/index.html` directly in your browser (double-click it, or right-click → Open With → your browser). It's a static file that talks to the API running on port 5001.

Register a user, log in, and start logging practice sessions.

## Project structure

```
practice-tracker/
├── backend/
│   ├── app.py            <- Flask app + all API routes
│   ├── models.py         <- User and PracticeSession database models
│   ├── auth.py           <- JWT token generation + the @token_required decorator
│   └── requirements.txt
└── frontend/
    └── index.html        <- single-page UI (HTML/CSS/JS, no build step needed)
```


## API reference

| Method | Endpoint             | Auth required | Description                          |
|--------|-----------------------|:--------------:|---------------------------------------|
| POST   | `/api/register`       | No             | Create a new user account             |
| POST   | `/api/login`           | No             | Log in, returns a JWT                 |
| GET    | `/api/sessions`        | Yes            | List the logged-in user's sessions    |
| POST   | `/api/sessions`        | Yes            | Log a new practice session            |
| PUT    | `/api/sessions/<id>`   | Yes            | Update a session (must own it)        |
| DELETE | `/api/sessions/<id>`   | Yes            | Delete a session (must own it)        |
| GET    | `/api/stats`           | Yes            | Aggregate stats (total time, by song) |
| GET    | `/api/profile`         | Yes            | Get the logged-in user's profile      |
| PUT    | `/api/profile`         | Yes            | Update bio, picture, skill level, genre |
| GET    | `/api/suggestions`     | Yes            | Curated practice suggestions (filter with `?skill_level=&genre=&type=`) |

Protected routes expect: `Authorization: Bearer <token>`


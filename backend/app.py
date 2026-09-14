from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, PracticeSession
from auth import generate_token, token_required
from suggestions_data import get_suggestions
from itunes_lookup import lookup_song
from datetime import datetime, timedelta, timezone
import os

app = Flask(__name__)
CORS(app)  # allows the frontend (served from a different port) to call this API

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'practice_tracker.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-secret-change-this-in-production"  # placeholder for a learning project

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# AUTH ROUTES
# ---------------------------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id, app.config["SECRET_KEY"])
    return jsonify({"token": token, "user": user.to_dict()}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()

    # Deliberately vague error message on purpose: don't reveal whether the
    # username or the password was wrong. This is a real security practice —
    # it prevents attackers from using your login form to discover which
    # usernames exist in the system (username enumeration).
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = generate_token(user.id, app.config["SECRET_KEY"])
    return jsonify({"token": token, "user": user.to_dict()}), 200


# ---------------------------------------------------------------------------
# PRACTICE SESSION ROUTES (all protected — require a valid JWT)
# ---------------------------------------------------------------------------

@app.route("/api/sessions", methods=["GET"])
@token_required
def get_sessions(current_user_id):
    sessions = (
        PracticeSession.query.filter_by(user_id=current_user_id)
        .order_by(PracticeSession.date.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in sessions]), 200


@app.route("/api/sessions", methods=["POST"])
@token_required
def create_session(current_user_id):
    data = request.get_json(force=True) or {}
    song_or_skill = data.get("song_or_skill", "").strip()
    duration_minutes = data.get("duration_minutes")
    notes = data.get("notes", "")
    session_type = data.get("session_type", "song")

    if not song_or_skill or not duration_minutes:
        return jsonify({"error": "song_or_skill and duration_minutes are required"}), 400

    try:
        duration_minutes = int(duration_minutes)
    except (ValueError, TypeError):
        return jsonify({"error": "duration_minutes must be a number"}), 400

    if session_type not in {"song", "fingerstyle", "lick", "scale", "technique", "other"}:
        session_type = "other"

    session = PracticeSession(
        user_id=current_user_id,
        song_or_skill=song_or_skill,
        duration_minutes=duration_minutes,
        notes=notes,
        session_type=session_type,
    )
    db.session.add(session)
    db.session.commit()
    return jsonify(session.to_dict()), 201


@app.route("/api/sessions/<int:session_id>", methods=["PUT"])
@token_required
def update_session(current_user_id, session_id):
    session = PracticeSession.query.filter_by(id=session_id, user_id=current_user_id).first()
    if not session:
        # Returning 404 (not 403) here on purpose: it doesn't confirm to a
        # caller whether a session with that id exists at all for someone
        # else's account.
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json(force=True) or {}
    if "song_or_skill" in data:
        session.song_or_skill = data["song_or_skill"]
    if "duration_minutes" in data:
        session.duration_minutes = int(data["duration_minutes"])
    if "notes" in data:
        session.notes = data["notes"]

    db.session.commit()
    return jsonify(session.to_dict()), 200


@app.route("/api/sessions/<int:session_id>", methods=["DELETE"])
@token_required
def delete_session(current_user_id, session_id):
    session = PracticeSession.query.filter_by(id=session_id, user_id=current_user_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404

    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "Session deleted"}), 200


@app.route("/api/stats", methods=["GET"])
@token_required
def get_stats(current_user_id):
    """Aggregate stats: total minutes, session count, per-song breakdown,
    current practice streak (consecutive days), and minutes practiced
    in the last 7 days."""
    sessions = PracticeSession.query.filter_by(user_id=current_user_id).all()

    total_minutes = sum(s.duration_minutes for s in sessions)
    total_sessions = len(sessions)

    by_song = {}
    for s in sessions:
        by_song[s.song_or_skill] = by_song.get(s.song_or_skill, 0) + s.duration_minutes

    # --- Streak calculation ---
    # Get the distinct calendar dates (ignoring time-of-day) the user practiced on,
    # most recent first, then count how many consecutive days back from
    # today (or yesterday, if they haven't practiced yet today) they go.
    practice_dates = sorted({s.date.date() for s in sessions}, reverse=True)

    streak = 0
    if practice_dates:
        today = datetime.now(timezone.utc).replace(tzinfo=None).date()
        expected = today

        for d in practice_dates:
            if d == expected:
                streak += 1
                expected -= timedelta(days=1)
            elif d == expected + timedelta(days=1):
                # Handles the case where they haven't logged anything today
                # yet but practiced yesterday — streak should still count.
                continue
            else:
                break

    # --- Weekly progress ---
    week_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
    minutes_this_week = sum(s.duration_minutes for s in sessions if s.date >= week_ago)

    return jsonify({
        "total_minutes": total_minutes,
        "total_sessions": total_sessions,
        "total_hours": round(total_minutes / 60, 1),
        "minutes_by_song": by_song,
        "current_streak": streak,
        "minutes_this_week": minutes_this_week,
    }), 200


# ---------------------------------------------------------------------------
# PROFILE ROUTES
# ---------------------------------------------------------------------------

@app.route("/api/profile", methods=["GET"])
@token_required
def get_profile(current_user_id):
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@app.route("/api/profile", methods=["PUT"])
@token_required
def update_profile(current_user_id):
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(force=True) or {}

    if "bio" in data:
        # Cap length so a user can't store something absurdly large in the DB
        user.bio = (data["bio"] or "")[:1000]

    if "profile_picture" in data:
        pic = data["profile_picture"] or ""
        # Rough sanity cap (~2MB base64) so a single profile picture can't
        # balloon the SQLite file uncontrollably. A production app would
        # instead upload to object storage (S3, etc.) and store just a URL.
        if len(pic) > 2_800_000:
            return jsonify({"error": "Image too large — please use a smaller photo"}), 400
        user.profile_picture = pic

    if "skill_level" in data:
        if data["skill_level"] in {"beginner", "intermediate", "advanced"}:
            user.skill_level = data["skill_level"]

    if "favorite_genre" in data:
        user.favorite_genre = (data["favorite_genre"] or "")[:50]

    if "weekly_goal_minutes" in data:
        try:
            goal = int(data["weekly_goal_minutes"])
            if 0 < goal <= 10000:
                user.weekly_goal_minutes = goal
        except (ValueError, TypeError):
            pass

    db.session.commit()
    return jsonify(user.to_dict()), 200


# ---------------------------------------------------------------------------
# SUGGESTIONS ROUTE
# ---------------------------------------------------------------------------

@app.route("/api/suggestions", methods=["GET"])
@token_required
def suggestions(current_user_id):
    """
    Returns curated practice suggestions, enriched with real song metadata
    (album artwork, preview clip, artist) from the iTunes Search API where
    available. Defaults to the logged-in user's own skill level unless a
    different one is explicitly requested via query params.
    """
    user = db.session.get(User, current_user_id)

    skill_level = request.args.get("skill_level", user.skill_level if user else None)
    genre = request.args.get("genre") or None
    session_type = request.args.get("type") or None
    search = request.args.get("search") or None

    results = get_suggestions(skill_level=skill_level, genre=genre, session_type=session_type, search=search)

    # Enrich each result with real song data where we have a title/artist to search for.
    # Failures here are non-fatal (see itunes_lookup.py) — a suggestion just
    # won't have artwork if the lookup fails or there's no internet.
    enriched = []
    for s in results:
        item = dict(s)
        if s.get("search_title"):
            song_data = lookup_song(s["search_title"], s.get("artist"))
            item["song_data"] = song_data  # None if lookup failed/found nothing
        else:
            item["song_data"] = None
        enriched.append(item)

    return jsonify(enriched), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)

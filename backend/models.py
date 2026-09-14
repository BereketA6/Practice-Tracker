from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """
    A registered user. Passwords are never stored in plain text —
    we store a salted hash instead, and check against it on login.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Profile fields
    bio = db.Column(db.Text, nullable=True)
    # Stored as a base64 data URL (e.g. "data:image/png;base64,...."). Fine for
    # a learning project; a production app would store an uploaded file in
    # cloud storage (S3, etc.) and save only the URL here instead.
    profile_picture = db.Column(db.Text, nullable=True)
    skill_level = db.Column(db.String(20), default="beginner")  # beginner | intermediate | advanced
    favorite_genre = db.Column(db.String(50), nullable=True)
    weekly_goal_minutes = db.Column(db.Integer, default=120)  # default: 2 hours/week

    # One user has many practice sessions (one-to-many relationship)
    sessions = db.relationship(
        "PracticeSession", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        # Explicitly use pbkdf2:sha256 instead of the werkzeug default (scrypt).
        # scrypt requires OpenSSL with scrypt support; Apple's system Python
        # ships with LibreSSL, which doesn't support it, causing an
        # AttributeError on Mac. pbkdf2:sha256 is universally supported.
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
            "bio": self.bio,
            "profile_picture": self.profile_picture,
            "skill_level": self.skill_level,
            "favorite_genre": self.favorite_genre,
            "weekly_goal_minutes": self.weekly_goal_minutes,
        }


class PracticeSession(db.Model):
    """
    A single logged practice session belonging to a user.
    Foreign key ties it back to the user who created it, so users
    can only ever see and modify their own sessions.
    """
    __tablename__ = "practice_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    song_or_skill = db.Column(db.String(200), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    # song | fingerstyle | lick | scale | technique | other
    session_type = db.Column(db.String(20), default="song")

    def to_dict(self):
        return {
            "id": self.id,
            "song_or_skill": self.song_or_skill,
            "duration_minutes": self.duration_minutes,
            "notes": self.notes,
            "date": self.date.isoformat(),
            "session_type": self.session_type,
        }

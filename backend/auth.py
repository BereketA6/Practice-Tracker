import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app

# In a real production app this would come from an environment variable,
# never hardcoded. Kept simple here for a learning project.
JWT_EXPIRY_HOURS = 24


def generate_token(user_id, secret_key):
    """Create a signed JWT that proves who the user is, without the server
    needing to store session state anywhere (this is what makes JWT auth
    'stateless' — any server instance can verify the token on its own)."""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


def token_required(f):
    """
    Decorator that protects a route: it checks for a valid JWT in the
    Authorization header before letting the request through, and injects
    the authenticated user's id as the first argument to the route function.

    Usage:
        @app.route("/sessions")
        @token_required
        def get_sessions(current_user_id):
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired, please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated

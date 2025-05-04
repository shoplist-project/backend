from flask import request, jsonify, session
from routes import api, login_required
from services.user_service import UserService


@api.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing required fields: username and password"}), 400

    username = data["username"]
    password = data["password"]

    user = UserService.create_user(username, password)

    if user is None:
        return jsonify({"error": "Username already exists"}), 409

    return jsonify(
        {
            "id": user.id,
            "username": user.username,
        }
    ), 201


@api.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing required fields: username and password"}), 400

    username = data["username"]
    password = data["password"]

    user = UserService.authenticate_user(username, password)

    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user.id
    session["username"] = user.username

    return jsonify({"id": user.id, "username": user.username}), 200


@api.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@api.route("/api/auth/me", methods=["GET"])
@login_required.login_required
def get_current_user():
    """
    Returns the currently authenticated user's information.
    Requires the user to be logged in (authenticated).
    """
    user_id = session.get("user_id")

    user = UserService.get_user_by_id(user_id)

    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user.id, "username": user.username}), 200

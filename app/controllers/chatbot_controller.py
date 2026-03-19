"""Chatbot route adapter.

Keeps existing /chat endpoint for frontend compatibility,
while delegating all response logic to the chatbot service layer.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.services.chatbot import chatbot_reply_from_user

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    """Compatibility endpoint used by the chatbot page JS."""
    if not current_user.is_student:
        return jsonify({"reply": "Chatbot is available for students only."}), 403

    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()
    if not user_message:
        return jsonify({"reply": "Please provide a message."}), 400

    try:
        response = chatbot_reply_from_user(user_message, current_user)
        return jsonify({"reply": response})
    except Exception:
        return jsonify({"reply": "Something went wrong."}), 500

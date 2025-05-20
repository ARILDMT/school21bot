from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models import db, PeerReviewSlot, User

pr_bp = Blueprint("pr_bp", __name__)

@pr_bp.route("/slots", methods=["POST"])
def create_slot():
    data = request.json
    login = data.get("login")
    time_str = data.get("scheduled_time")

    user = User.query.filter_by(school21_login=login).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        scheduled_time = datetime.fromisoformat(time_str)
    except Exception:
        return jsonify({"error": "Invalid datetime format"}), 400

    slot = PeerReviewSlot(scheduled_time=scheduled_time, owner=user)
    db.session.add(slot)
    db.session.commit()

    return jsonify({"message": "Slot created", "slot_id": slot.id})

@pr_bp.route("/slots", methods=["GET"])
def list_slots():
    slots = PeerReviewSlot.query.all()
    return jsonify([
        {
            "id": s.id,
            "scheduled_time": s.scheduled_time.isoformat(),
            "owner": s.owner.school21_login,
            "booked_by": s.booked_by.school21_login if s.booked_by else None
        }
        for s in slots
    ])

@pr_bp.route("/slots/<int:slot_id>/book", methods=["POST"])
def book_slot(slot_id):
    data = request.json
    login = data.get("login")

    user = User.query.filter_by(school21_login=login).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    slot = PeerReviewSlot.query.get(slot_id)
    if not slot or slot.booked_by:
        return jsonify({"error": "Slot not available"}), 400

    slot.booked_by = user
    db.session.commit()

    return jsonify({"message": "Slot booked"})

@pr_bp.route("/slots/<int:slot_id>/cancel", methods=["POST"])
def cancel_slot(slot_id):
    slot = PeerReviewSlot.query.get(slot_id)
    if not slot:
        return jsonify({"error": "Slot not found"}), 404

    slot.booked_by = None
    db.session.commit()
    return jsonify({"message": "Slot canceled"})

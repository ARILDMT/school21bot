from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models import db, PeerReviewSlot, User

pr_bp = Blueprint("pr_bp", __name__)

# Создать новый слот
@pr_bp.route("/create_slot", methods=["POST"])
def create_slot():
    data = request.json
    user_login = data.get("login")
    timestamp = data.get("timestamp")

    if not user_login or not timestamp:
        return jsonify({"error": "login and timestamp are required"}), 400

    user = User.query.filter_by(school21_login=user_login).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M")
        slot = PeerReviewSlot(owner_id=user.id, datetime_slot=dt)
        db.session.add(slot)
        db.session.commit()
        return jsonify({"message": "Slot created", "slot_id": slot.id}), 201
    except Exception as e:
        return jsonify({"error": "Invalid timestamp format", "details": str(e)}), 400

# Получить все слоты
@pr_bp.route("/slots", methods=["GET"])
def get_slots():
    slots = PeerReviewSlot.query.all()
    return jsonify([
        {
            "id": slot.id,
            "owner": slot.owner.school21_login,
            "datetime": slot.datetime_slot.isoformat(),
            "booked_by": slot.booked_by.school21_login if slot.booked_by else None
        }
        for slot in slots
    ])

# Забронировать слот
@pr_bp.route("/book_slot", methods=["POST"])
def book_slot():
    data = request.json
    login = data.get("login")
    slot_id = data.get("slot_id")

    if not login or not slot_id:
        return jsonify({"error": "login and slot_id are required"}), 400

    user = User.query.filter_by(school21_login=login).first()
    slot = PeerReviewSlot.query.get(slot_id)

    if not user or not slot:
        return jsonify({"error": "User or slot not found"}), 404

    if slot.booked_by_id:
        return jsonify({"error": "Slot already booked"}), 400

    slot.booked_by_id = user.id
    db.session.commit()

    return jsonify({"message": "Slot booked"}), 200

# Отменить бронь
@pr_bp.route("/cancel_slot", methods=["POST"])
def cancel_slot():
    data = request.json
    slot_id = data.get("slot_id")

    slot = PeerReviewSlot.query.get(slot_id)
    if not slot:
        return jsonify({"error": "Slot not found"}), 404

    slot.booked_by_id = None
    db.session.commit()

    return jsonify({"message": "Slot unbooked"}), 200

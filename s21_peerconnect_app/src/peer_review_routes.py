# peer_review_routes.py
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from src.models import db, User, PeerReviewSlot
from src.s21_api_client import get_valid_access_token # To ensure user is authenticated with S21

# Helper to get user_login (placeholder for actual session/auth mechanism)
# This should be consistent with how user_login is retrieved in s21_routes.py
# For now, we assume a user_login is passed, and we find the User object by it.
def get_current_db_user_from_request():
    user_login = request.args.get("user_login") # For GET
    if not user_login and request.is_json:
        user_login = request.json.get("user_login") # For POST/PUT
    
    if not user_login:
        return None, (jsonify({"error": "User login not provided"}), 400)
        
    user = User.query.filter_by(school21_login=user_login).first()
    if not user:
        return None, (jsonify({"error": "User not found in database"}), 404)
    return user, None

pr_bp = Blueprint("pr_bp", __name__)

@pr_bp.route("/slots", methods=["POST"])
def create_slot():
    user, error = get_current_db_user_from_request()
    if error: return error[0], error[1]

    # Optional: Check if user has a valid S21 token, as a prerequisite to creating slots
    # s21_access_token = get_valid_access_token(user.school21_login)
    # if not s21_access_token:
    #     return jsonify({"error": "User not authenticated with School21 or token expired"}), 401

    data = request.json
    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    project_name = data.get("project_name")

    if not start_time_str or not end_time_str:
        return jsonify({"error": "start_time and end_time are required"}), 400

    try:
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
    except ValueError:
        return jsonify({"error": "Invalid datetime format. Use ISO format."}), 400

    if start_time >= end_time:
        return jsonify({"error": "start_time must be before end_time"}), 400

    # Check for overlapping slots for the same creator (optional, good to have)
    existing_slot = PeerReviewSlot.query.filter(
        PeerReviewSlot.creator_user_id == user.id,
        PeerReviewSlot.start_time < end_time,
        PeerReviewSlot.end_time > start_time,
        PeerReviewSlot.status != "cancelled"
    ).first()

    if existing_slot:
        return jsonify({"error": "An overlapping slot already exists for this time period."}), 409

    slot = PeerReviewSlot(
        creator_user_id=user.id,
        start_time=start_time,
        end_time=end_time,
        project_name=project_name,
        status="available"
    )
    db.session.add(slot)
    db.session.commit()
    current_app.logger.info(f"User {user.school21_login} created slot {slot.id}")
    return jsonify(slot.to_dict()), 201

@pr_bp.route("/slots", methods=["GET"])
def get_slots():
    # No specific user needed to view all available/booked slots, but could be filtered
    # For example, by month, by creator, by status
    month_str = request.args.get("month") # YYYY-MM format
    status_filter = request.args.get("status")
    creator_login = request.args.get("creator_login")

    query = PeerReviewSlot.query

    if month_str:
        try:
            year, month = map(int, month_str.split("-"))
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            query = query.filter(PeerReviewSlot.start_time >= start_date, PeerReviewSlot.start_time < end_date)
        except ValueError:
            return jsonify({"error": "Invalid month format. Use YYYY-MM"}), 400
    
    if status_filter:
        query = query.filter(PeerReviewSlot.status == status_filter)
    
    if creator_login:
        creator_user = User.query.filter_by(school21_login=creator_login).first()
        if creator_user:
            query = query.filter(PeerReviewSlot.creator_user_id == creator_user.id)
        else:
            return jsonify({"error": f"Creator user {creator_login} not found"}), 404
            
    slots = query.order_by(PeerReviewSlot.start_time.asc()).all()
    return jsonify([slot.to_dict() for slot in slots]), 200

@pr_bp.route("/slots/<int:slot_id>/book", methods=["POST"])
def book_slot(slot_id):
    booker_user, error = get_current_db_user_from_request()
    if error: return error[0], error[1]

    slot = PeerReviewSlot.query.get(slot_id)
    if not slot:
        return jsonify({"error": "Slot not found"}), 404

    if slot.status != "available":
        return jsonify({"error": "Slot is not available for booking"}), 409
    
    if slot.creator_user_id == booker_user.id:
        return jsonify({"error": "Cannot book your own slot"}), 400

    slot.booker_user_id = booker_user.id
    slot.status = "booked"
    db.session.commit()
    current_app.logger.info(f"User {booker_user.school21_login} booked slot {slot.id} created by user_id {slot.creator_user_id}")
    return jsonify(slot.to_dict()), 200

@pr_bp.route("/slots/<int:slot_id>/cancel", methods=["POST"])
def cancel_slot(slot_id):
    # This could be more nuanced: only creator can cancel an available slot,
    # or creator/booker can cancel a booked slot (maybe with conditions)
    current_user, error = get_current_db_user_from_request()
    if error: return error[0], error[1]

    slot = PeerReviewSlot.query.get(slot_id)
    if not slot:
        return jsonify({"error": "Slot not found"}), 404

    if slot.creator_user_id != current_user.id and slot.booker_user_id != current_user.id:
        return jsonify({"error": "You are not authorized to cancel this slot"}), 403
    
    if slot.status == "cancelled" or slot.status == "completed":
        return jsonify({"error": f"Slot is already {slot.status} and cannot be cancelled"}), 409

    # Logic for who can cancel what:
    # If user is creator: can cancel if 'available' or 'booked' (notifies booker if booked)
    # If user is booker: can cancel if 'booked' (notifies creator)
    previous_status = slot.status
    slot.status = "cancelled"
    # If it was booked, we might want to clear the booker_user_id or keep it for history
    # For now, let's keep it for simplicity to know who had booked it.
    
    db.session.commit()
    current_app.logger.info(f"User {current_user.school21_login} cancelled slot {slot.id} (previous status: {previous_status})")
    # TODO: Implement notifications to the other party if the slot was booked.
    return jsonify(slot.to_dict()), 200

# Add other slot management routes as needed (e.g., update slot details, mark as completed)


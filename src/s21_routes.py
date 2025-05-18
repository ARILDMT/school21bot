# s21_routes.py
from flask import Blueprint, jsonify, request, current_app
from functools import wraps
import jwt # PyJWT for decoding access token to get user_login if needed

from src.s21_api_client import make_school21_api_request
from src.models import User, db # Assuming User model is in src.models

s21_data_bp = Blueprint("s21_data_bp", __name__)

# --- Token Verification Decorator (Optional but good practice) ---
# This decorator would typically be used if the client sends its own JWT to our backend
# For now, we assume our backend identifies the user through a session or a passed user_login/telegram_id
# and then uses the stored refresh_token to get a School21 access_token.

# For simplicity, our API endpoints will require a `user_login` to be passed in the request (e.g., from a session or a secure frontend call)
# or derive it from a frontend-sent JWT if we implement that later.

# Helper to get user_login (placeholder for actual session/auth mechanism)
def get_current_user_login_from_request():
    # In a real app, you might get this from a session cookie, a JWT sent by your frontend, etc.
    # For now, let's assume it might be passed as a query parameter or in JSON body for simplicity in testing.
    # THIS IS NOT SECURE FOR PRODUCTION WITHOUT PROPER AUTH ON THESE ENDPOINTS THEMSELVES.
    user_login = request.args.get("user_login") # For GET
    if not user_login and request.is_json:
        user_login = request.json.get("user_login") # For POST/PUT
    if not user_login:
        # As a fallback, if an Authorization: Bearer <OUR_OWN_JWT> is sent by frontend
        # we could decode it. This is more advanced.
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                # Assuming OUR_OWN_JWT contains school21_login in its payload
                # You would need a secret key for this JWT, same as used for its creation
                # decoded_token = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
                # user_login = decoded_token.get("school21_login")
                pass # Placeholder for actual JWT decoding
            except jwt.ExpiredSignatureError:
                return None, ("Token expired", 401)
            except jwt.InvalidTokenError:
                return None, ("Invalid token", 401)
    return user_login, None

@s21_data_bp.route("/me", methods=["GET"])
def get_my_profile():
    user_login, error_response = get_current_user_login_from_request()
    if error_response:
        return jsonify({"error": error_response[0]}), error_response[1]
    if not user_login:
        return jsonify({"error": "User login not provided or identifiable from request"}), 400

    # The School21 OpenAPI spec doesn't explicitly list a "/v1/users/me" or similar generic "me" endpoint.
    # It has /v1/participants/{login}
    # So, we will use that, assuming 'user_login' is the participant's login.
    endpoint = f"/v1/participants/{user_login}"
    
    api_response, status_code = make_school21_api_request(user_login, endpoint, method="GET")
    
    if status_code == 200 and api_response:
        return jsonify(api_response), 200
    else:
        return jsonify(api_response or {"error": "Failed to fetch profile data"}), status_code or 500

@s21_data_bp.route("/myprojects", methods=["GET"])
def get_my_projects():
    user_login, error_response = get_current_user_login_from_request()
    if error_response:
        return jsonify({"error": error_response[0]}), error_response[1]
    if not user_login:
        return jsonify({"error": "User login not provided or identifiable from request"}), 400

    endpoint = f"/v1/participants/{user_login}/projects"
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)
    status = request.args.get("status") # Optional: ASSIGNED, REGISTERED, IN_PROGRESS, IN_REVIEWS, ACCEPTED, FAILED

    params = {"limit": limit, "offset": offset}
    if status:
        params["status"] = status
        
    api_response, status_code = make_school21_api_request(user_login, endpoint, method="GET", params=params)
    
    if status_code == 200 and api_response:
        return jsonify(api_response), 200
    else:
        return jsonify(api_response or {"error": "Failed to fetch projects data"}), status_code or 500

# Add more routes here for other School21 API data based on the OpenAPI spec and bot commands:
# e.g., /myskills, /mybadges, /logtime, /mylevel, /myxp (points)

@s21_data_bp.route("/mypoints", methods=["GET"])
def get_my_points(): # Corresponds to /myxp
    user_login, error_response = get_current_user_login_from_request()
    if error_response:
        return jsonify({"error": error_response[0]}), error_response[1]
    if not user_login:
        return jsonify({"error": "User login not provided or identifiable from request"}), 400

    endpoint = f"/v1/participants/{user_login}/points"
    api_response, status_code = make_school21_api_request(user_login, endpoint, method="GET")
    if status_code == 200 and api_response:
        return jsonify(api_response), 200
    else:
        return jsonify(api_response or {"error": "Failed to fetch points data (XP)"}), status_code or 500

@s21_data_bp.route("/mylevel", methods=["GET"])
def get_my_level():
    user_login, error_response = get_current_user_login_from_request()
    if error_response:
        return jsonify({"error": error_response[0]}), error_response[1]
    if not user_login:
        return jsonify({"error": "User login not provided or identifiable from request"}), 400
    
    # The OpenAPI spec for /v1/participants/{login} returns level information directly.
    endpoint = f"/v1/participants/{user_login}"
    api_response, status_code = make_school21_api_request(user_login, endpoint, method="GET")
    if status_code == 200 and api_response:
        # Extract level related info if needed, or return the whole participant object
        level_info = {
            "level": api_response.get("level"), 
            "levelSystemId": api_response.get("levelSystemId")
        }
        return jsonify(level_info), 200
    else:
        return jsonify(api_response or {"error": "Failed to fetch level data"}), status_code or 500

# ... other S21 data endpoints ...


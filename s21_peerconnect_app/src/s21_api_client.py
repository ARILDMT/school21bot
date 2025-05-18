# s21_api_client.py
import requests
import time
from datetime import datetime, timedelta
from flask import current_app, jsonify

from src.models import db, User # Assuming User model is in src.models

SCHOOL21_API_BASE_URL = "https://edu-api.21-school.ru/services/21-school/api"
SCHOOL21_TOKEN_URL = "https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token"
SCHOOL21_CLIENT_ID = "s21-open-api"

def get_valid_access_token(user_login: str):
    """ 
    Retrieves a valid access token for the given user. 
    Handles token refresh if the current token is expired or nearing expiration.
    Returns the access_token string or None if an error occurs.
    """
    user = User.query.filter_by(school21_login=user_login).first()
    if not user:
        current_app.logger.error(f"User not found: {user_login}")
        return None

    refresh_token = user.get_refresh_token()
    if not refresh_token:
        current_app.logger.error(f"No refresh token found for user: {user_login}")
        return None # User needs to re-authenticate

    # Check if access token is still valid (e.g., has at least 5 minutes left)
    # For simplicity, we will try to refresh if expires_at is not set or in the past.
    # A more robust check would be if user.access_token_expires_at < datetime.utcnow() + timedelta(minutes=5)
    # However, we don't store the access_token itself in the DB in the current User model.
    # The current design implies we fetch a new access_token using refresh_token for each sequence of API calls
    # or if the frontend explicitly requests a new one. 
    # For now, let's assume we always try to get a fresh access_token using refresh_token if needed.

    payload = {
        "client_id": SCHOOL21_CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        current_app.logger.info(f"Attempting to refresh access token for user: {user_login}")
        response = requests.post(SCHOOL21_TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        
        new_access_token = token_data.get("access_token")
        new_refresh_token = token_data.get("refresh_token") # Important: refresh token might be rotated
        expires_in = token_data.get("expires_in", 3600)

        if not new_access_token:
            current_app.logger.error(f"Refresh token grant did not return an access_token for user {user_login}. Response: {token_data}")
            return None

        # Update user's refresh token (if rotated) and expiry time
        if new_refresh_token:
            user.set_refresh_token(new_refresh_token)
        user.access_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        db.session.commit()
        current_app.logger.info(f"Successfully refreshed access token for user: {user_login}")
        return new_access_token

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Failed to refresh access token for user {user_login}: {e}")
        if e.response is not None:
            current_app.logger.error(f"Refresh token API response status: {e.response.status_code}, body: {e.response.text}")
            # If refresh token is invalid (e.g., 400 Bad Request with specific error), user might need to re-login
            if e.response.status_code == 400:
                 # Potentially clear the invalid refresh token from DB or mark user as needing re-auth
                 pass # For now, just log
        return None

def make_school21_api_request(user_login: str, endpoint: str, method: str = "GET", params: dict = None, data: dict = None):
    """
    Makes an authenticated request to the School21 API.
    `endpoint` should be the path after the base URL (e.g., /v1/users/me).
    Returns the JSON response or None if an error occurs.
    """
    access_token = get_valid_access_token(user_login)
    if not access_token:
        # Could return a specific error structure instead of None
        return None, 401 # Unauthorized or token refresh failed

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json" # Assuming JSON for most S21 API interactions
    }
    url = f"{SCHOOL21_API_BASE_URL}{endpoint}"
    
    current_app.logger.info(f"Making School21 API {method} request to {url} for user {user_login}")
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, params=params, json=data)
        # Add other methods (PUT, DELETE) as needed
        else:
            current_app.logger.error(f"Unsupported HTTP method: {method}")
            return None, 500
            
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as e:
        current_app.logger.error(f"School21 API request failed for user {user_login} to {url}: {e}")
        current_app.logger.error(f"School21 API response status: {e.response.status_code}, body: {e.response.text}")
        # Attempt to parse error response from School21 API
        error_details = e.response.text
        try:
            error_details = e.response.json()
        except ValueError:
            pass
        return {"error": "School21 API request failed", "details": error_details, "status_code": e.response.status_code}, e.response.status_code
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"School21 API request failed for user {user_login} to {url} (network/other error): {e}")
        return {"error": "School21 API request failed due to network or other issue", "details": str(e)}, 500


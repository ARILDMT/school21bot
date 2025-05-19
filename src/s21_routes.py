import os
import requests
from flask import Blueprint, jsonify, request
from src.models import User

s21_data_bp = Blueprint("s21_data_bp", __name__)

SCHOOL21_API_URL = os.getenv("SCHOOL21_API_URL", "https://edu-api.21-school.ru/services/21-school/api")

@s21_data_bp.route("/user/<login>", methods=["GET"])
def get_user_data(login):
    user = User.query.filter_by(school21_login=login).first()
    if not user:
        return jsonify({"error": "User not found in database"}), 404

    access_token = request.headers.get("Authorization")
    if not access_token:
        return jsonify({"error": "Missing Authorization token"}), 401

    try:
        url = f"{SCHOOL21_API_URL}/v2/users/{login}"
        headers = {"Authorization": access_token}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return jsonify(res.json())
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch user data", "details": str(e)}), 500

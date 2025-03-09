from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Dummy login endpoint for admin users.
    Expected JSON:
    {
        "username": "admin",
        "password": "password"
    }
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if username == "admin" and password == "password":
        access_token = create_access_token(identity=username, expires_delta=datetime.timedelta(hours=1))
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

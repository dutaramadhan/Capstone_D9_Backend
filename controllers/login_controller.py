from flask import jsonify, Blueprint, request
from config import Config
import jwt
import datetime

login_controller = Blueprint('login_controller', __name__)

@login_controller.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']

        if not username or not password:
            return jsonify({"error": "Username and password are required", "status_code" : 400}), 400
        if username == Config.USERNAME and password == Config.PASSWORD:
            token = jwt.encode({
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, Config.SECRET_KEY, algorithm="HS256")
            return jsonify({"message": "Login successful", "token": token, "status_code": 200}), 200
        else:
            return jsonify({"error": "Invalid username or password", "status_code": 401}), 401
    except Exception as e:
        return jsonify({"error": str(e), "status code": 500}), 500
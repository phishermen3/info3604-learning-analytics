import os
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, current_user

from App.controllers import (
    create_log,
    get_logs,
    send_to_lrs,
    load_json
)

log_views = Blueprint('log_views', __name__, template_folder='../templates')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@log_views.route('/log', methods=['POST'])
@jwt_required()
def send_statement():
    data = request.get_json()
    user_code = current_user.user_code
    statement, code = create_log(user_code, data.get("verb"), data.get("activity"))
    
    if code != 201:
        return jsonify(statement), code
        
    success, error = send_to_lrs(statement)
    
    if not success:
        current_app.logger.error(f"Error statement not sent: {error}")
    
    return jsonify(statement), code

@log_views.route('/logs', methods=['GET'])
@jwt_required()
def get_statements():
    logs, code = get_logs(current_user.user_code)
    return jsonify(logs), code

@log_views.route('/api/data', methods=['GET'])
def get_api_data():
    verbs = load_json(os.path.join(BASE_DIR, "xapi", "verbs.json"))
    activities = load_json(os.path.join(BASE_DIR, "xapi", "activities.json"))
    return jsonify({"verbs": verbs, "activities": activities})
from flask import Blueprint, jsonify, request, current_app

from App.controllers import (
    create_log,
    get_logs,
    send_to_lrs
)

log_views = Blueprint('log_views', __name__, template_folder='../templates')

@log_views.route('/log', methods=['POST'])
def send_statement():
    data = request.get_json()
    statement, code = create_log(data.get("verb"), data.get("activity"))
    success, error = send_to_lrs(statement)
    
    if not success:
        current_app.logger.error(f"Error statement not sent: {error}")
    
    return jsonify(statement), code

@log_views.route('/logs', methods=['GET'])
def get_statements():
    logs, code = get_logs()
    return jsonify(logs), code
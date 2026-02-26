from flask import Blueprint, jsonify, request

from App.controllers import (
    create_log,
    get_logs
)

log_views = Blueprint('log_views', __name__, template_folder='../templates')

@log_views.route('/log', methods=['POST'])
def send_statement():
    data = request.get_json()
    statement, code = create_log(data.get("verb"), data.get("activity"))
    return jsonify(statement), code

@log_views.route('/logs', methods=['GET'])
def get_statements():
    logs, code = get_logs()
    return jsonify(logs), code
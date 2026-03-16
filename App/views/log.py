from App.controllers.log import load_course_registry
from flask_login import current_user
from flask import Blueprint, jsonify, request, current_app, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user, get_csrf_token
import os

from App.controllers import (
    create_log,
    get_logs,
    send_to_lrs,
    load_json
)

log_views = Blueprint('log_views', __name__, template_folder='../templates')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@log_views.route("/home")
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    return render_template("index.html", current_user_id=user_id)

@log_views.route('/log', methods=['POST'])
@jwt_required(locations=["cookies"])
def send_statement():
    data = request.get_json()
    user_code = current_user.user_code

    statement, code = create_log(
        user_code, 
        data.get("course_id"),
        data.get("verb_name"), 
        data.get("activity_name"),
        data.get("team_id"),
        data.get("project_id"),
        data.get("pedagogical_stage"),
        data.get("problem_step")
    )

    if code != 201:
        return jsonify(statement), code
        
    success, error = send_to_lrs(statement)
    
    if not success:
        current_app.logger.error(f"Error statement not sent: {error}")
        return jsonify({"error": error}), 500
    
    return jsonify(statement), code

@log_views.route('/logs', methods=['GET'])
@jwt_required()
def get_statements():
    course_id = request.args.get("course")
    if not course_id:
        return jsonify({"error": "Course ID required"}), 400
    
    logs, code = get_logs(current_user.user_code, course_id)
    return jsonify(logs), code

@log_views.route('/api/data', methods=['GET'])
def get_api_data():
    course_id = request.args.get("course_id")

    registry = load_course_registry(course_id)

    verbs = registry.get("verbs", {})
    activities = registry.get("activities", {})

    problem_steps = registry.get("problem_steps", {})
    problem_step_names = list(problem_steps.keys())
    step_definitions = {k: v["definition"] for k, v in problem_steps.items()}

    stages = registry.get("stages", {})
    stage_names = list(stages.keys())
    stage_definitions = {k: v["definition"] for k, v in stages.items()}

    return jsonify({"verbs": verbs, "activities": activities, 
                    "problem_steps": problem_step_names, "step_definitions": step_definitions,
                    "stages": stage_names, "stage_definitions": stage_definitions})

@log_views.route("/csrf-token", methods=["GET"])
@jwt_required(locations=["cookies"])
def get_csrf():
    return jsonify({"csrf_token": get_csrf_token()})
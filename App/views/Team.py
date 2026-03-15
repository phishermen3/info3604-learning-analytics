from flask import Blueprint, request, render_template, jsonify
from types import SimpleNamespace
import random, string

team_bp = Blueprint("Team", __name__)

courses = {1: "Test Course"}
teams = {}

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@team_bp.route("/courses/<int:course_id>/teams", methods=["POST"])
def create_team(course_id: int):
    current_user = getattr(create_team, "current_user", SimpleNamespace(is_authenticated=False, id=None))
    
    if course_id not in courses:
        return jsonify({"error": "Course not found"}), 404
    
    data = request.get_json() or {}
    team_name = data.get("team_name")
    
    if not team_name:
        return jsonify({"error": "team_name is required"}), 400
    
    team_id = len(teams) + 1
    team_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    teams[team_id] = {"id": team_id, "name": team_name, "course": course_id, "code": team_code}
    
    return jsonify({
        "team id": team_id,
        "team code": team_code,
        "course": course_id
    }), 201

@team_bp.route("/teams/join", methods=["POST"])
def join_team():
    current_user = getattr(join_team, "current_user", SimpleNamespace(is_authenticated=False, id=None))
    
    if not current_user or not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json() or {}
    code = data.get("team_code")
    
    if not code:
        return jsonify({"error": "team_code is required"}), 400
    
    for team in teams.values():
        if team["code"] == code:
            return jsonify({"message": f"Joined team {team['name']}"}), 200
    
    return jsonify({"error": "Team code invalid"}), 404
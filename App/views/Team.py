from App.controllers import team as team_controller
from flask import Blueprint, request, jsonify, g

team_bp = Blueprint("Team", __name__)

@team_bp.route("/courses/<string:course_id>/teams", methods=["POST"])
def create_team(course_id):    
    current_user = getattr(g, "current_user", None)
    if not current_user or not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        team = team_controller.create_team(course_id)
        return jsonify({
            "team_id": team.id,
            "team_code": team.team_code,
            "course_id": team.course_id
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@team_bp.route("/teams/join", methods=["POST"])
def join_team():
    current_user = getattr(g, "current_user", None)
    if not current_user or not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json() or {}
    team_code = data.get("team_code")
    
    if not team_code:
        return jsonify({"error": "team_code is required"}), 400
    
    try:
        team = team_controller.join_team(team_code)
        return jsonify({
            "message": f"Joined team {team.team_code}",
            "team_id": team.id,
            "team_code": team.team_code
        }), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 401
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
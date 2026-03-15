from App.controllers import team as team_controller
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user

team_views = Blueprint("Team", __name__)

@team_views.route("/courses/<string:course_id>/teams", methods=["POST"])
@jwt_required(locations=["cookies"])
def create_team(course_id):        
    try:
        team = team_controller.create_team(course_id)
        return jsonify({
            "team_id": team.id,
            "team_code": team.team_code,
            "course_id": team.course_id
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@team_views.route("/teams/join", methods=["POST"])
@jwt_required(locations=["cookies"])
def join_team():    
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
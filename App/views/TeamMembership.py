from flask import Blueprint, jsonify, g
from App.controllers import teamMembership as team_membership_controller 

teamMembership_views = Blueprint("TeamMembership", __name__)

@teamMembership_views.route("/courses/<string:course_id>/<string:team_id>/membership", methods=["GET"])
def check_membership(course_id, team_id):
    current_user = getattr(g, "current_user", None)
    
    if not current_user or not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    already_member = team_membership_controller.check_membership(team_id=team_id, user_id=current_user.id)

    if already_member:
        return jsonify({"error": "User already belongs to team"}), 409

    is_enrolled = any(c.id == course_id for c in current_user.enrolled_courses)

    return jsonify({"enrolled": is_enrolled}), 200
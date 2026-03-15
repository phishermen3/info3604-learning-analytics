from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user
from App.controllers import teamMembership as team_membership_controller 

teamMembership_views = Blueprint("TeamMembership", __name__)

@teamMembership_views.route("/courses/<string:course_id>/<string:team_id>/membership", methods=["GET"])
def check_membership(course_id, team_id):
    user = current_user
    already_member = team_membership_controller.check_membership(team_id=team_id, user_id=user.id)

    if already_member:
        return jsonify({"error": "User already belongs to team"}), 409

    is_enrolled = any(c.id == course_id for c in user.enrolled_courses)

    return jsonify({"enrolled": is_enrolled}), 200
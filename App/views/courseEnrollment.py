from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from App.controllers import courseEnrollment as course_enrollment_controller 

courseEnrollment_views = Blueprint("CourseEnrollment", __name__)

@courseEnrollment_views.route("/api/enrolled", methods=["POST"])
@jwt_required()
def check_enrollment():
    course_id = request.args.get("course_id")

    if not course_id:
        return jsonify({"error": "course_id required"}), 400

    enrolled = course_enrollment_controller.is_user_enrolled(course_id)

    return jsonify({"enrolled": enrolled})

@courseEnrollment_views.route("/api/course-info", methods=["GET"])
@jwt_required()
def get_course_info():
    course_id = request.args.get("course_id")
    team, project = course_enrollment_controller.get_course_info(course_id)

    if not team or not project:
        return jsonify({"team_id": None, "project_id": None}), 200

    return jsonify({"team_id": team.id, "project_id": project.id})
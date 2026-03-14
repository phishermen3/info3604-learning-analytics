from flask import Blueprint, jsonify, request
from App.controllers import courseEnrollment as course_enrollment_controller 

courseEnrollment_views = Blueprint("CourseEnrollment", __name__)

@courseEnrollment_views.route("/api/enrolled", methods=["POST"])
def check_enrollment():
    course_id = request.args.get("course_id")

    if not course_id:
        return jsonify({"error": "course_id required"}), 400

    enrolled = course_enrollment_controller.is_user_enrolled(course_id)

    return jsonify({"enrolled": enrolled})
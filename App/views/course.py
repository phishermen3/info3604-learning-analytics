from flask import Blueprint, jsonify, request
from flask_login import current_user
from flask import jsonify

course_views = Blueprint("Course", __name__)

courses = [
    {"id": "COMP3608", "name": "Intelligent Systems"},
    {"id": "INFO3607", "name": "Fundamentals of WAN Technology"},
] 

@course_views.route("/courses", methods=["GET"])
def list_courses():
    return jsonify(courses), 200

@course_views.route("/courses/<string:course_id>", methods=["GET"])
def get_course_by_id(course_id):
    for course in courses:
        if course["id"] == course_id:
            return jsonify({"course id": course["id"], "course name": course["name"]}), 200
    return jsonify({"message": "Error: Course code invalid"}), 404

@course_views.route("/api/enrolled", methods=["GET"])
def check_enrollment():
    course_id = request.args.get("course_id")
    user = current_user

    enrolled = any(c.id == course_id for c in user.enrolled_courses)
    return jsonify({"enrolled": enrolled}), 200

from flask import Blueprint
from flask import render_template
from flask import jsonify

course_bp = Blueprint("Course", __name__)

courses = [
    {"id": 1, "name": "Intelligent Systems"},
    {"id": 2, "name": "WAN"},
] 

@course_bp.route("/courses", methods=["GET"])
def list_courses():
    return jsonify(getattr(list_courses, "courses")), 200

@course_bp.route("/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    courses = getattr(get_course, "courses")
    for course in courses:
        if course["id"] == course_id:
            return jsonify({"course id": course["id"], "course name": course["name"]}), 200
    return jsonify({"message": "Error: Course code invalid"}), 401
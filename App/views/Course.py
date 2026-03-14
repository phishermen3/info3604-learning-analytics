from flask import Blueprint
from flask import render_template
from flask import jsonify

course_bp = Blueprint("Course", __name__)

courses = [
    {"id": "COMP3608", "name": "Intelligent Systems"},
    {"id": "INFO3607", "name": "Fundamentals of WAN Technology"},
] 

@course_bp.route("/courses", methods=["GET"])
def list_courses():
    return jsonify(courses), 200

@course_bp.route("/courses/<string:course_id>", methods=["GET"])
def get_course_by_id(course_id):
    for course in courses:
        if course["id"] == course_id:
            return jsonify({"course id": course["id"], "course name": course["name"]}), 200
    return jsonify({"message": "Error: Course code invalid"}), 404
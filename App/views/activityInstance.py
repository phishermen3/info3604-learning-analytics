from App.controllers import activityInstance as activity_controller
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user

instance_views = Blueprint("ActivityInstance", __name__)

@instance_views.route("/api/instances", methods=["POST"])
@jwt_required(locations=["cookies"])
def create_instance(): 
    data = request.json
    activity_type = data["activity_type"]
    display_name = data.get("display_name", "New Task")
    course_id = data["course_id"]
    team_id = data["team_id"]
    project_id = data["project_id"]
    created_by = data["user_code"]

    try:
        instance = activity_controller.create_activity_instance(
            activity_type, 
            display_name, 
            course_id, 
            team_id, 
            project_id, 
            created_by
        )
        return jsonify(instance.get_json()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@instance_views.route("/api/projects/<string:project_id>/instances", methods=["GET"])
@jwt_required(locations=["cookies"])
def get_instances(project_id):
    try:
        instances = activity_controller.get_activity_instances(project_id)
        return jsonify(instances), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

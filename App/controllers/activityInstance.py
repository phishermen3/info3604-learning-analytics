from App.database import db
from App.models import ActivityInstance

def create_activity_instance(activity_type, display_name, course_id, team_id, project_id, created_by):
    try:
        instance = ActivityInstance(activity_type, display_name, course_id, team_id, project_id, created_by)
        db.session.add(instance)
        db.session.commit()
        return instance
    except Exception as e:
        db.session.rollback()
        return ValueError(f"Failed to create instance: {str(e)}")

def get_activity_instances(project_id):
    instances = ActivityInstance.query.filter_by(project_id=project_id).all()
    if not instances:
        return []
    return [instance.get_json() for instance in instances]
from App.database import db
from datetime import datetime, timezone
import uuid

class ActivityInstance(db.Model):
    __tablename__ = "activity_instances"

    id = db.Column(db.String(36), primary_key=True)
    activity_type = db.Column(db.String(255), nullable=False)  
    display_name = db.Column(db.String(255), nullable=False)

    course_id = db.Column(db.String(8), nullable=False)
    team_id = db.Column(db.String(36), nullable=False)
    project_id = db.Column(db.String, nullable=False)

    created_by = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__ (self, activity_type, display_name, course_id, team_id, project_id, created_by):
        self.id = str(uuid.uuid4())
        self.activity_type = activity_type
        self.display_name = display_name
        self.course_id = course_id
        self.team_id = team_id
        self.project_id = project_id
        self.created_by = created_by

    def get_json(self):
        return {
            "id": self.id,
            "activity_type": self.activity_type,
            "display_name": self.display_name,
            "course_id": self.course_id,
            "team_id": self.team_id,
            "project_id": self.project_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat()
        }
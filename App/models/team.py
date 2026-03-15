import uuid
from App.database import db

class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = db.Column(db.String(8), db.ForeignKey('courses.id'), nullable=False)
    team_code = db.Column(db.String(8), nullable=False, unique=True, index=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    memberships = db.relationship('TeamMembership', backref='team', lazy=True, cascade="all, delete-orphan")
    project = db.relationship("Project", backref="team", uselist=False)

    def __init__(self, course_id, team_code, created_by):
        self.course_id = course_id
        self.team_code = team_code
        self.created_by = created_by
        
    def get_json(self):
        return{
            'id': self.id,
            'course_id': self.course_id,
            'team_code': self.team_code,
            'created_by': self.created_by
        }
        
    def get_context_parent(self):
        return{
            "objectType": "Activity",
            "id": f"https://logstack.azurewebsites.net/projects/{self.course_id}/{self.team_code}",
            "definition": {
                "name": { "en-US": f"{self.course_id} Project - Team {self.team_code}" },
                "description": { "en-US": f"{self.course_id} Project instance for Team {self.team_code}" }
            }
        }
        
    def get_context_grouping(self):
        return{
            "objectType": "Activity",   
            "id": f"https://logstack.azurewebsites.net/groups/{self.team_code}",
            "definition": {               
                "name": { "en-US": self.team_code },
                "description": { "en-US": f"Team {self.team_code}" }
            }
        }

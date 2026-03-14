import uuid
from App.database import db
from sqlalchemy import CheckConstraint

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = db.Column(db.String(8), db.ForeignKey('courses.id'), nullable=False)
    team_id = db.Column(db.String(8), db.ForeignKey('teams.id'), nullable=False)
    grade = db.Column(db.Float, nullable=True)
    
    __table_args__ = (
        CheckConstraint('grade >= 0 AND grade <= 100', name='check_grade_range'),
    )

    def __init__(self, course_id, team_id):
        self.course_id = course_id
        self.team_id = team_id

    def add_grade(self, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be a percentage between 0 and 100")
        self.grade = value
        
    def get_json(self):
        return{
            'id': self.id,
            'course_id': self.course_id,
            'team_id': self.team_id,
            'grade': self.grade
        }
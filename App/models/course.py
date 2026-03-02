from App.database import db

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    teams = db.relationship('Team', backref='course', lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, id, name):
        self.id = id
        self.name = name
        
    def get_json(self):
        return{
            'id': self.id,
            'name': self.name
        }
        
    def get_context_category(self):
        return{
            "objectType": "Activity",   
            "id": f"https://logstack.azurewebsites.net/courses/{self.id}",
            "definition": {               
                "name": { "en-US": self.id },
                "description": { "en-US": self.name }
            }
        }

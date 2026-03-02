from App.database import db

class TeamMembership(db.Model):
    __tablename__ = "team_members"
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), primary_key=True)
    
    def __init__(self, user_id, team_id):
        self.user_id = user_id
        self.team_id = team_id
        
    def get_json(self):
        return{
            'user_id': self.user_id,
            'team_id': self.team_id
        }

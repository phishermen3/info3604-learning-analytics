import random, string
from App.models import Team, Course, TeamMembership
from App.database import db
from flask import g

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_team(course_id):
    course = Course.query.get(course_id)
    if not course:
        raise ValueError("Course not found")    
    
    team_code = generate_code()
    
    team = Team(course_id=course_id, team_code=team_code, created_by=g.current_user.id)
    db.session.add(team)
    db.session.commit()
    
    return team

def join_team(team_code):    
    team = Team.query.filter_by(team_code=team_code).first()
    if not team:
        raise ValueError("Invalid team code")
    
    if any(m.user_id == g.current_user.id for m in team.memberships):
        return team

    membership = TeamMembership(user_id=g.current_user.id, team_id=team.id)
    db.session.add(membership)
    db.session.commit()
    
    return team
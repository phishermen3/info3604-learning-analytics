import random, string
from App.models import Team, Course, TeamMembership, Project
from App.database import db
from flask_jwt_extended import jwt_required, current_user

MAX_TEAM_SIZE = 4

def generate_code(length=6):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Team.query.filter_by(team_code=code).first():
            return code

def create_team(course_id):
    course = Course.query.get(course_id)
    if not course:
        raise ValueError("Course not found")   

    existing = TeamMembership.query.join(Team).filter(
        TeamMembership.user_id == current_user.id,
        Team.course_id == course_id
    ).first()

    if existing:
        raise ValueError("User already belongs to a team in this course") 
    
    team_code = generate_code()
    
    team = Team(course_id=course_id, team_code=team_code, created_by=current_user.id)
    db.session.add(team)
    db.session.flush()   

    membership = TeamMembership(user_id=current_user.id, team_id=team.id)
    db.session.add(membership)

    project = Project(team_id=team.id)
    db.session.add(project)

    db.session.commit()
    
    return team

def join_team(team_code):    
    team = Team.query.filter_by(team_code=team_code).first()
    if not team:
        raise ValueError("Invalid team code")
    
    for membership in current_user.memberships:
        if membership.team.course_id == team.course_id:
            raise ValueError("User already belongs to a team in this course")
    
    if len(team.memberships) >= MAX_TEAM_SIZE:
        raise ValueError("Team is full")

    membership = TeamMembership(user_id=current_user.id, team_id=team.id)
    db.session.add(membership)
    db.session.commit()
    
    return team
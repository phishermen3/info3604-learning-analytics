from .user import create_user
from App.models import Course, Team, TeamMembership, Project, CourseEnrollment
from App.database import db

def initialize():
    db.drop_all()
    db.create_all()

    # Create Bob
    bob = create_user('bob', 'bobpass')

    # Create courses
    course = Course(id="INFO3607", name="Fundamentals of WAN Technologies")
    db.session.add(course)

    course = Course(id="COMP3608", name="Intelligent Systems")
    db.session.add(course)
    db.session.flush()
    
    # Enroll Bob in a course
    enrollment = CourseEnrollment(user_id=bob.id, course_id="INFO3607")
    db.session.add(enrollment)

    enrollment = CourseEnrollment(user_id=bob.id, course_id="COMP3608")
    db.session.add(enrollment)

    # Create a team for the course
    team = Team(course_id="INFO3607", team_code="teamcode", created_by=bob.id)
    db.session.add(team)
    db.session.flush()

    # Add Bob to the team
    membership = TeamMembership(user_id=bob.id, team_id=team.id)
    db.session.add(membership)

    # Create a project for the team
    project = Project(team_id=team.id)
    db.session.add(project)

    db.session.commit()



    steve = create_user('steve', 'stevepass')
    enrollment = CourseEnrollment(user_id=steve.id, course_id="COMP3608")
    db.session.add(enrollment)

    team = Team(course_id="COMP3608", team_code="teamteam", created_by=steve.id)
    db.session.add(team)
    db.session.flush()

    membership = TeamMembership(user_id=steve.id, team_id=team.id)
    db.session.add(membership)

    project = Project(team_id=team.id)
    db.session.add(project)

    db.session.commit()



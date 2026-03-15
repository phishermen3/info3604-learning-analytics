from App.models import CourseEnrollment, Team, TeamMembership, Project
from App.database import db
from flask_jwt_extended import current_user

def enroll_user(course_id):
    existing = CourseEnrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if existing:
        return existing

    enrollment = CourseEnrollment(
        user_id=current_user.id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()
    return True

def is_user_enrolled(course_id):
    return CourseEnrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first() is not None

def get_course_info(course_id):
    user = current_user

    membership = TeamMembership.query.join(Team).filter(
        Team.course_id == course_id,
        TeamMembership.user_id == user.id
    ).first()

    if not membership:
        return None, None
    
    team = membership.team
    project = Project.query.filter_by(team_id=team.id).first()

    return team, project

def get_enrolled_courses():
    user = current_user
    enrolled_courses = CourseEnrollment.query.filter_by(user_id=user.id).all()
    return [{"id": ec.course_id} for ec in enrolled_courses] 
from App.models import CourseEnrollment
from App.database import db
from flask import g

def enroll_user(course_id):
    existing = CourseEnrollment.query.filter_by(
        user_id=g.current_user.id,
        course_id=course_id
    ).first()

    if existing:
        return existing

    enrollment = CourseEnrollment(
        user_id=g.current_user.id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()
    return True

def is_user_enrolled(course_id):
    return CourseEnrollment.query.filter_by(
        user_id=g.current_user.id,
        course_id=course_id
    ).first() is not None
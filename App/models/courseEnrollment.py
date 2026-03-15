from App.database import db

class CourseEnrollment(db.Model):
    __tablename__ = "course_enrollments"

    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(db.String(8), db.ForeignKey('courses.id'), primary_key=True)

    def __init__(self, user_id, course_id):
        self.user_id = user_id
        self.course_id = course_id

    def get_json(self):
        return{
            'user_id': self.user_id,
            'course_id': self.course_id
        }
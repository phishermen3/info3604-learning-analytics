from App.models import User
from App.database import db

def create_user(user_code, password):
    newuser = User(user_code=user_code, password=password)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def get_user_by_code(user_code):
    result = db.session.execute(db.select(User).filter_by(user_code=user_code))
    return result.scalar_one_or_none()

def get_user(id):
    return db.session.get(User, id)

def get_all_users():
    return db.session.scalars(db.select(User)).all()

def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

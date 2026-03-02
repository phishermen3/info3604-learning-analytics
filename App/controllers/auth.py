import secrets
from datetime import timedelta
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, JWTManager, 
    get_jwt_identity, 
    verify_jwt_in_request
  )

from App.models import User
from App.database import db

def signup(password):
  if password:
    user_code = generate_unique_code()
    new_user = User(user_code=user_code, password=password)
    db.session.add(new_user)
    db.session.commit()
    access_token = create_access_token(identity=str(new_user.id), )
    refresh_token = create_refresh_token(identity=str(new_user.id))
    return access_token, refresh_token
  return None, None

def login(user_code, password, remember=False):
  result = db.session.execute(db.select(User).filter_by(user_code=user_code))
  user = result.scalar_one_or_none()
  if user and user.check_password(password):
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=15))
    if remember:
      refresh_expires = timedelta(days=14)
    else:
      refresh_expires = timedelta(hours=2)
    refresh_token = create_refresh_token(identity=str(user.id), expires_delta=refresh_expires)
    return access_token, refresh_token
  return None, None


def setup_jwt(app):
  jwt = JWTManager(app)

  # Always store a string user id in the JWT identity (sub),
  # whether a User object or a raw id is passed.
  @jwt.user_identity_loader
  def user_identity_lookup(identity):
    user_id = getattr(identity, "id", identity)
    return str(user_id) if user_id is not None else None

  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.get(User, identity)

  return jwt


# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          identity = get_jwt_identity()
          current_user = db.session.get(User, identity) if identity else None
          is_authenticated = current_user is not None
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)

#8-digit code generator  
def generate_unique_code():
  while True:
    code = secrets.token_hex(4)
    if not User.query.filter_by(user_code=code).first():
      return code
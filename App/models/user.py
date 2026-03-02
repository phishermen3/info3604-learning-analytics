import uuid
from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_code =  db.Column(db.String(8), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, user_code, password):
        self.user_code = user_code
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'user_code': self.user_code,
            'created_at': self.created_at.isoformat()
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


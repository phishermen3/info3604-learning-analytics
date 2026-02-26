import os
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import JSONB
from App.database import db

load_dotenv()

env = os.getenv("ENV")
if env == "PRODUCTION":
    json_type = JSONB
else:
    json_type = db.JSON

class Log(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    actor = db.Column(db.String(50), nullable=False)
    verb_id = db.Column(db.String(256), nullable=False)
    verb_name = db.Column(db.String(50), nullable=False)
    object = db.Column(json_type, nullable=False)
    context = db.Column(json_type, nullable=False)
    
    def __init__(self, id, actor, verb_id, verb_name, object, context):
        self.id = id
        self.actor = actor
        self.verb_id = verb_id
        self.verb_name = verb_name
        self.object = object
        self.context = context
    
    def get_json(self):
        return{
            "id": self.id,
            "actor": {
                "objectType": "Agent",
                "account": {
                    "homePage": "https://logstack.azurewebsites.net",
                    "name": self.actor
                }
            },
            "verb": {
                "id": self.verb_id,
                "display": {"en-US": self.verb_name}
            },
            "object": self.object,
            "context": self.context
        }
    
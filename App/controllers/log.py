import json, requests, uuid, os
from tincan import RemoteLRS, Statement
from App.models import Log
from App.database import db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def create_log(verb, activity):
    verbs = load_json(os.path.join(BASE_DIR, "xapi", "verbs.json"))
    activities = load_json(os.path.join(BASE_DIR, "xapi", "activities.json"))
    
    if verb not in verbs:
        return {"error": "Invalid verb"}, 400
    
    if activity not in activities:
        return {"error": "Invalid artefact"}, 400
    
    statement_id = str(uuid.uuid4())
    actor = "temp_user"
    verb_id = verbs[verb].get("id")
    verb_name = verbs[verb].get("display", {}).get("en-US")
    activity_object = activities[activity]
    pedagogical_stage = verbs[verb].get("extensions", {}).get("https://yourdomain.com/xapi/extensions/pedagogical-stage")


    context_data = {
        "contextActivities": {

            "parent": [
                {
                    "objectType": "Activity",
                    "id": "https://yourapp.edu/projects/wan/group-A",
                    "definition": {
                        "name": { "en-US": "WAN Project - Group A" },
                        "description": { "en-US": "WAN Project instance for Group A" }
                    }
                }
            ],

            "grouping": [
                {
                    "objectType": "Activity",   
                    "id": "https://yourapp.edu/groups/group-A",
                    "definition": {               
                        "name": { "en-US": "Group A" },
                        "description": { "en-US": "INFO 3607 Project Group A" }
                    }
                }
            ],

            "category": [
                {
                    "objectType": "Activity",
                    "id": "https://yourapp.edu/courses/INFO-3607",
                    "definition": {
                        "name": { "en-US": "INFO 3607" },
                        "description": { "en-US": "Fundamentals of WAN Tech" }
                    }
                }
            ]
        },

        "extensions": {
            "https://yourapp.edu/extensions/pedagogical-stage": pedagogical_stage,
            "https://yourapp.edu/extensions/problem-step": "verification",
            "https://yourapp.edu/extensions/logging-mode": "pedagogy"
        }
    }

    new_log = Log(
        id=statement_id,
        actor=actor,
        verb_id=verb_id,
        verb_name=verb_name,
        object=activity_object,
        context=context_data
    )

    db.session.add(new_log)
    db.session.commit()

    return new_log.get_json(), 201

def get_logs():
    logs = Log.query.all()
    response = []
    
    for log in logs:
        statement = log.get_json()
        
        activity_name = log.object["definition"]["name"]["en-US"]
        stage = log.context["extensions"].get("https://yourapp.edu/extensions/pedagogical-stage")
        
        summary = f"{log.actor} {log.verb_name} {activity_name} (Stage: {stage})"
        
        response.append({
            "summary": summary,
            "statement": statement
        })
        
    return response, 200

def send_to_lrs(statement):
    lrs_endpoint = os.getenv("LRS_ENDPOINT")
    username = os.getenv("LRS_USERNAME")
    password = os.getenv("LRS_PASSWORD")
    
    lrs = RemoteLRS(
        endpoint=lrs_endpoint,
        version='1.0.3',
        username=username,
        password=password
    )
    
    response = lrs.save_statement(Statement(statement))
    
    if response.success:
        return True, None
    else:
        return False, response.content
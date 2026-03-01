import json, uuid, os
from tincan import RemoteLRS, Statement
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

lrs_endpoint = os.getenv("LRS_ENDPOINT")
username = os.getenv("LRS_USERNAME")
password = os.getenv("LRS_PASSWORD")

lrs = RemoteLRS(
        endpoint=lrs_endpoint,
        version='1.0.3',
        username=username,
        password=password
    )

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
    activity = activities[activity]
    pedagogical_stage = verbs[verb].get("extensions", {}).get("https://yourdomain.com/xapi/extensions/pedagogical-stage")


    context = {
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

    statement = {
        "id": statement_id,
            "actor": {
                "objectType": "Agent",
                "account": {
                    "homePage": "https://logstack.azurewebsites.net",
                    "name": actor
                }
            },
            "verb": {
                "id": verb_id,
                "display": {"en-US": verb_name}
            },
            "object": activity,
            "context": context
    }

    return statement, 201

def get_logs():
    query = {
        "limit": 10,
        "since": "2026-02-28T00:01:13Z"
    }
    
    response = lrs.query_statements(query)
    
    if not response.success:
        return response.content, 500
    
    results = []
    
    while True:
        statements = response.content.statements
    
        for stmt in statements:
            summary = f"({stmt.actor.account.name} {stmt.verb.display['en-US']} {stmt.object.definition.name['en-US']} (Stage: {stmt.context.extensions['https://yourapp.edu/extensions/pedagogical-stage']})"
            
            results.append({
                "summary": summary,
                "statement": stmt.to_json()
            })
            
        more_url = response.content.more
        
        if not more_url:
            break
        
        response = lrs.more_statements(more_url)
        
        if not response.success:
            return response.content, 500
        
    return results, 200

def send_to_lrs(statement):
    response = lrs.save_statement(Statement(statement))
    
    if response.success:
        return True, None
    else:
        return False, response.content
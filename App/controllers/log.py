import json, uuid, os
from App.models import User, TeamMembership
from tincan import RemoteLRS, Statement, Agent
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_lrs():
    lrs_endpoint = os.getenv("LRS_ENDPOINT")
    username = os.getenv("LRS_USERNAME")
    password = os.getenv("LRS_PASSWORD")
    
    return RemoteLRS(
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

def create_log(user_code, verb, activity):
    verbs = load_json(os.path.join(BASE_DIR, "xapi", "verbs.json"))
    activities = load_json(os.path.join(BASE_DIR, "xapi", "activities.json"))
    
    if verb not in verbs:
        return {"error": "Invalid verb"}, 400
    
    if activity not in activities:
        return {"error": "Invalid artefact"}, 400
    
    statement_id = str(uuid.uuid4())
    actor = user_code
    verb_id = verbs[verb].get("id")
    verb_name = verbs[verb].get("display", {}).get("en-US")
    activity = activities[activity]
    pedagogical_stage = verbs[verb].get("extensions", {}).get("https://logstack.azurewebsites.net/extensions/pedagogical-stage")
    problem_step = verbs[verb].get("extensions", {}).get("https://logstack.azurewebsites.net/extensions/problem-step")

    

    context = {
        "contextActivities": {
            "parent": [
                {
                    "objectType": "Activity",
                    "id": "https://logstack.azurewebsites.net/projects/wan/group-A",
                    "definition": {
                        "name": { "en-US": "WAN Project - Group A" },
                        "description": { "en-US": "WAN Project instance for Group A" }
                    }
                }
            ],

            "grouping": [
                {
                    "objectType": "Activity",   
                    "id": "https://logstack.azurewebsites.net/groups/group-A",
                    "definition": {               
                        "name": { "en-US": "Group A" },
                        "description": { "en-US": "INFO 3607 Project Group A" }
                    }
                }
            ],

            "category": [
                {
                    "objectType": "Activity",
                    "id": "https://logstack.azurewebsites.net/courses/INFO-3607",
                    "definition": {
                        "name": { "en-US": "INFO 3607" },
                        "description": { "en-US": "Fundamentals of WAN Tech" }
                    }
                }
            ]
        },

        "extensions": {
            "https://logstack.azurewebsites.net/extensions/pedagogical-stage": pedagogical_stage,
            "https://logstack.azurewebsites.net/extensions/problem-step": problem_step,
            "https://logstack.azurewebsites.net/extensions/logging-mode": "pedagogy"
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

def get_logs(user_code):
    agent = Agent(
        account={
            "homePage": "https://logstack.azurewebsites.net",
            "name": user_code
        }
    )
    
    query = {
        "agent": agent,
        "limit": 10,
        "since": "2026-03-05T00:00:00Z"
    }
    
    lrs = get_lrs()
    
    response = lrs.query_statements(query)
    
    if not response.success:
        return response.content, 500
    
    results = []
    
    while True:
        statements = response.content.statements
    
        for stmt in statements:
            summary = f"{stmt.actor.account.name} {stmt.verb.display['en-US']} {stmt.object.definition.name['en-US']} (Stage: {stmt.context.extensions['https://logstack.azurewebsites.net/extensions/pedagogical-stage']})"
            
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
    lrs = get_lrs()
    response = lrs.save_statement(Statement(statement))
    
    if response.success:
        return True, None
    else:
        return False, response.content
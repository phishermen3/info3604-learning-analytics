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
    pedagogical_stage = verbs[verb].get("extensions", {}).get("https://yourdomain.com/xapi/extensions/pedagogical-stage")

    user = User.query.filter_by(user_code=user_code).first()
    
    if not user:
        return {"error": "User not found"}, 404
    
    membership = TeamMembership.query.filter_by(user_id=user.id).first()
    
    if not membership:
        return {"error": "User is not a member of a team for this course"}, 400
    
    team = membership.team
    course = team.course

    context = {
        "contextActivities": {
            "parent": [team.get_context_parent()],
            "grouping": [team.get_context_grouping()],
            "category": [course.get_context_category()]
        },

        "extensions": {
            "https://logstack.azurewebsites.net/extensions/pedagogical-stage": pedagogical_stage,
            "https://logstack.azurewebsites.net/extensions/problem-step": "verification",
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
        "since": "2026-02-28T00:01:13Z"
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
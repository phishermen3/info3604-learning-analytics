import json, uuid, os, base64
from App.models import Course, Project, Team
from tincan import RemoteLRS, Statement, Agent
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSES_DIR = os.path.join(BASE_DIR, "xapi")

LOGSTACK_BASE = "https://logstack.azurewebsites.net"

PEDAGOGICAL_STAGE_URL = f"{LOGSTACK_BASE}/extensions/pedagogical-stage"
PROBLEM_STEP_URL = f"{LOGSTACK_BASE}/extensions/problem-step"
LOGGING_MODE_URL = f"{LOGSTACK_BASE}/extensions/logging-mode"

_cache = {}

def load_course_registry(course_id):
    if course_id in _cache:
        return _cache[course_id]

    course_path = os.path.join(COURSES_DIR, course_id)

    verbs = load_json(os.path.join(course_path, "verbs.json"))
    activities = load_json(os.path.join(course_path, "activities.json"))
    problem_steps = load_json(os.path.join(course_path, "steps.json"))
    stages = load_json(os.path.join(COURSES_DIR, "stages.json"))

    _cache[course_id] = {
        "verbs": verbs,
        "activities": activities,
        "problem_steps": problem_steps,
        "stages": stages
    }

    return _cache[course_id]

# -----------------------------------
# LRS Functions
# -----------------------------------

def get_lrs():
    lrs_endpoint = os.getenv("LRS_ENDPOINT")
    username = os.getenv("LRS_USERNAME")
    password = os.getenv("LRS_PASSWORD")

    if not lrs_endpoint or not username or not password:
        raise ValueError("LRS configuration missing")

    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    
    return RemoteLRS(
        endpoint=lrs_endpoint,
        version='1.0.3',
        auth=f"Basic {auth}"
    )

def send_to_lrs(statement):
    try:
        lrs = get_lrs()
        response = lrs.save_statement(Statement(statement))
        
        if response.success:
            return True, None
        else:
            return False, response.content

    except Exception as e:
        return False, str(e)

# -----------------------------------
# Log Functions
# -----------------------------------

def create_log(user_code, course_id, verb_name, activity_name, team_id, project_id, pedagogical_stage, problem_step):
    registry = load_course_registry(course_id)
    
    verbs = registry.get("verbs", {})
    activities = registry.get("activities", {})
    problem_steps = registry.get("problem_steps", {})
    stages = registry.get("stages", {})

    if verb_name not in verbs:
        return {"error": "Invalid verb"}, 400
    
    if activity_name not in activities:
        return {"error": "Invalid activity"}, 400
    
    if pedagogical_stage not in stages:
        return {"error": "Invalid pedagogical stage"}, 400
    
    if problem_step not in problem_steps:
        return {"error": "Invalid problem step"}, 400
    
    verb_template = verbs[verb_name]
    verb = build_verb(verb_template)

    activity_template = activities[activity_name]
    activity = build_activity(activity_template, course_id, team_id, project_id)
    
    actor = build_actor(user_code)
    context = build_context(course_id, team_id, project_id, pedagogical_stage, problem_step)

    statement = {
        "id": str(uuid.uuid4()),
        "actor": actor,
        "verb": verb,
        "object": activity,
        "context": context
    }

    return statement, 201

def get_logs(user_code, course_id, scope="individual", team_code=None):    
    query = build_query(user_code, scope, team_code)
    if query is None:
        return [], 200
    
    lrs = get_lrs()
    response = lrs.query_statements(query)
    
    if not response.success:
        return response.content, 500
    
    results = []
    expected_course_id = f"{LOGSTACK_BASE}/courses/{course_id}"
    expected_team_code = f"{LOGSTACK_BASE}/groups/{team_code}" if team_code else None
    
    while True:
        statements = response.content.statements or []
        
        for stmt in statements:
            if not matches_scope(stmt, scope, expected_course_id, expected_team_code):
                continue

            try:
                results.append(format_statement(stmt))
            except (AttributeError, KeyError):
                return {"error": "Statement malformed"}, 500
        
        more_url = response.content.more
        if not more_url:
            break
        
        response = lrs.more_statements(more_url)
        if not response.success:
            return response.content, 500
        
    return results, 200


# -----------------------------------
# Log Builders
# -----------------------------------

def build_actor(user_code):
    return {
        "objectType": "Agent",
        "account": {
            "homePage": LOGSTACK_BASE,
            "name": user_code
        }
    }

def build_verb(verb_template):
    return {
        "id": verb_template["id"],
        "display": verb_template["display"]
    }

def build_activity(activity_template, course_id, team_id, project_id):
    activity_type = activity_template["id"].split("/")[-1]  
    instance_id = str(uuid.uuid4())
    definition = activity_template.get("definition", {})

    return {
        "objectType": "Activity",
        "id": f"{LOGSTACK_BASE}/projects/{course_id}/{team_id}/{project_id}/{activity_type}/{instance_id}",
        "definition": {
            "type": activity_template["id"],
            "name": definition.get("name"),
            "description": definition.get("description")
        }
    }


def build_context(course_id, team_id, project_id, pedagogical_stage, problem_step):
    team = Team.query.get(team_id)
    if not team:
        raise ValueError("Invalid team ID")

    project = Project.query.get(project_id)
    if not project:
        raise ValueError("Invalid project ID")

    course = Course.query.get(course_id)
    if not course:
        raise ValueError("Invalid course ID")
    
    return {
        "contextActivities": {
            "parent": team.get_context_parent(),
            "grouping": team.get_context_grouping(),
            "category": [
                {
                    "objectType": "Activity",
                    "id": f"{LOGSTACK_BASE}/courses/{course_id}",
                    "definition": {
                        "name": {"en-US": course.name},
                        "description": {"en-US": f"{course.name} course at the University of the West Indies"}
                    }
                }
            ]
        },
        "extensions": {
            PEDAGOGICAL_STAGE_URL: pedagogical_stage,
            PROBLEM_STEP_URL: problem_step,
            LOGGING_MODE_URL: "pedagogy"
        }
    }

# -----------------------------------
# Helper Functions
# -----------------------------------

def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}    
    
def build_query(user_code, scope, team_code):
    query = {"limit": 10}

    if scope == "individual":
        query["agent"] = Agent(
            account={
                "homePage": LOGSTACK_BASE,
                "name": user_code
            }
        )

    elif scope == "group":
        if not team_code:
            return None
        
        query["context"] = {
            "contextActivities": {
                "grouping": [
                    {
                        "objectType": "Activity",
                        "id": f"{LOGSTACK_BASE}/groups/{team_code}"
                    }
                ]
            }
        }

    return query

def matches_scope(stmt, scope, expected_course_id, expected_team_id):
    context = getattr(stmt, "context", None)
    context_activities = getattr(context, "context_activities", None)

    if not context_activities:
        return False

    def normalize(value):
        if not value:
            return []
        return value if isinstance(value, list) else [value]

    categories = normalize(getattr(context_activities, "category", []))
    groupings = normalize(getattr(context_activities, "grouping", []))

    course_match = any(act.id == expected_course_id for act in categories)
    team_match = any(act.id == expected_team_id for act in groupings)

    if scope == "group":
        return course_match and team_match
    return course_match

def format_statement(stmt):
    context = getattr(stmt, "context", None)
    exts = getattr(context, "extensions", {}) if context else {}

    actor_code = getattr(stmt.actor.account, "name", "Unknown")

    return {
        "user_code": actor_code,
        "verb_name": stmt.verb.display["en-US"],
        "activity_name": stmt.object.definition.name["en-US"],
        "stage": exts.get(f'{LOGSTACK_BASE}/extensions/pedagogical-stage'),
        "step": exts.get(f'{LOGSTACK_BASE}/extensions/problem-step'),
        "timestamp": getattr(stmt, "timestamp", None)
    }

# -----------------------------------
# Getters
# -----------------------------------

def get_course(course_id):
    course = Course.query.get(course_id)
    if course:
        return {"name": course.name}
    else:
        raise ValueError("Invalid course ID") 

def get_project(project_id):
    project = Project.query.get(project_id)
    if project:
        return {"name": project.name}
    else:
        raise ValueError("Invalid project ID") 

def get_team(team_id):
    team = Team.query.get(team_id)
    if team:
        return {"name": team.name}
    else:
        raise ValueError("Invalid team ID") 
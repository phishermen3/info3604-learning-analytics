import pytest
from flask import Flask
from types import SimpleNamespace
from App.views.team import team_views, create_team, join_team

#Pytest fixture
@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(team_views)
    with app.test_client() as client:
        yield client

#Tests
def test_create_team_course_not_found(client):
    create_team.current_user = SimpleNamespace(is_authenticated=True, id=1)
    response = client.post("/courses/9999/teams", json={"team_name": "Alpha"})
    assert response.status_code == 404
    assert response.get_json()["error"] == "Error: Course code invalid"

def test_create_team_missing_name(client):
    create_team.current_user = SimpleNamespace(is_authenticated=True, id=1)
    response = client.post("/courses/1/teams", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "team_code is required"

def test_create_team_success(client):
    create_team.current_user = SimpleNamespace(is_authenticated=True, id=1)
    response = client.post("/courses/1/teams", json={"team_name": "Alpha Team"})
    assert response.status_code == 201
    data = response.get_json()
    assert "team id" in data
    assert "team code" in data
    assert data["course"] == 1

def test_join_team_requires_auth(client):
    join_team.current_user = SimpleNamespace(is_authenticated=False, id=1)
    response = client.post("/teams/join", json={"team_code": "ABC123"})
    assert response.status_code == 401
"""
def test_join_team_success(client):
    team_id = len(team) + 1
    team[team_id] = {"id": team_id, "name": "Beta", "course": 1, "code": "ABC123"}
    
    join_team.current_user = SimpleNamespace(is_authenticated=True, id=1)
    response = client.post("/teams/join", json={"team_code": "ABC123"})
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
"""

def test_join_team_no_code(client):
    join_team.current_user = SimpleNamespace(is_authenticated=True, id=1)
    response = client.post("/teams/join", json={})
    assert response.status_code == 400

def test_join_team_invalid_code(client):
    join_team.current_user = SimpleNamespace(is_authenticated=True, id=1)
    response = client.post("/teams/join", json={"team_code": "WRONG"})
    assert response.status_code == 404
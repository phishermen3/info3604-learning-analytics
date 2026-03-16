import pytest
from flask import Flask
from types import SimpleNamespace
from App.views.teamMembership import teamMembership_views, check_membership

#Pytest fixture
@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(teamMembership_views)
    with app.test_client() as client:
        yield client

#Tests
def test_not_authenticated(client):
    check_membership.current_user = SimpleNamespace(is_authenticated=False, id=1)
    check_membership.session = None
    response = client.get("/courses/1/phishermen/membership")
    assert response.status_code == 401
    assert response.get_json == {"error": "Authentication required"}

def test_authenticated_enrolled(client):
    check_membership.current_user = SimpleNamespace(is_authenticated=True, id=42)
    class FakeSession:
        enrolled = True
        def close(self): pass
    check_membership.session = FakeSession()
    response = client.get("/courses/1/phishermen/membership")
    assert response.status_code == 200
    assert response.get_json == {"enrolled": True}

def test_authenticated_not_enrolled(client):
    check_membership.current_user = SimpleNamespace(is_authenticated=True, id=42)
    class FakeSession:
        enrolled = False
        def close(self): pass
    check_membership.session = FakeSession()
    response = client.get("/courses/1/phishermen/membership")
    assert response.status_code == 200
    assert response.get_json == {"enrolled": False}

def test_duplicate_membership(client):
    check_membership.current_user = SimpleNamespace(is_authenticated=True, id=50)
    check_membership.session = SimpleNamespace(
        memberships=[
            SimpleNamespace(user_id=50, course_id=10, team_id=2)
        ],
        enrolled=True,
        close=lambda: None
    )
    response = client.get("/courses/10/phishermen/membership")
    assert response.status_code == 409
    assert response.get_json()["error"] == \
        "User already belongs to team"

def test_not_duplicate_membership(client):
    check_membership.current_user = SimpleNamespace(
        is_authenticated=True,
        id=1
    )

    check_membership.session = SimpleNamespace(
        memberships=[
            SimpleNamespace(user_id=2, course_id=10, team_id=2)
        ],
        enrolled=False,
        close=lambda: None
    )

    response = client.get("/courses/10/phishermen/membership")

    assert response.status_code == 200
    assert response.get_json()["enrolled"] is False
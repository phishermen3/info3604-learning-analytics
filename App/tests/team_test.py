import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from unittest.mock import patch, MagicMock

from App.views.team import team_views


@pytest.fixture
def app():
    app = Flask(__name__)

    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "super-secret-testing-key-maximum-length"

    JWTManager(app)

    app.register_blueprint(team_views)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def login_cookie(client, app):
    with app.app_context():
        token = create_access_token(identity="test_user")

    client.set_cookie(
        key="access_token_cookie",
        value=token
    )



@patch("App.controllers.team.create_team")
def test_create_team_success(mock_create_team, client, app):
    login_cookie(client, app)

    mock_team = MagicMock()
    mock_team.id = 1
    mock_team.team_code = "ABC123"
    mock_team.course_id = "INFO2602"

    mock_create_team.return_value = mock_team

    response = client.post("/courses/INFO2602/teams")

    assert response.status_code == 201
    data = response.get_json()

    assert data["team_id"] == 1
    assert data["team_code"] == "ABC123"
    assert data["course_id"] == "INFO2602"


@patch("App.controllers.team.create_team")
def test_create_team_invalid_course(mock_create_team, client, app):
    login_cookie(client, app)

    mock_create_team.side_effect = ValueError("Course not found")

    response = client.post("/courses/BAD101/teams")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Course not found"


def test_create_team_unauthenticated(client):
    response = client.post("/courses/INFO2602/teams")

    assert response.status_code == 401



@patch("App.controllers.team.join_team")
def test_join_team_success(mock_join_team, client, app):
    login_cookie(client, app)

    mock_team = MagicMock()
    mock_team.id = 5
    mock_team.team_code = "JOIN456"

    mock_join_team.return_value = mock_team

    response = client.post(
        "/api/join-team",
        json={"team_code": "JOIN456"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Joined team JOIN456"
    assert data["team_id"] == 5
    assert data["team_code"] == "JOIN456"


def test_join_team_missing_team_code(client, app):
    login_cookie(client, app)

    response = client.post(
        "/api/join-team",
        json={}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "team_code is required"


@patch("App.controllers.team.join_team")
def test_join_team_invalid_code(mock_join_team, client, app):
    login_cookie(client, app)

    mock_join_team.side_effect = ValueError("Team not found")

    response = client.post(
        "/api/join-team",
        json={"team_code": "BADCODE"}
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Team not found"


@patch("App.controllers.team.join_team")
def test_join_team_not_enrolled(mock_join_team, client, app):
    login_cookie(client, app)

    mock_join_team.side_effect = PermissionError(
        "User not enrolled in this course"
    )

    response = client.post(
        "/api/join-team",
        json={"team_code": "JOIN456"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "User not enrolled in this course"


def test_join_team_unauthenticated(client):
    response = client.post(
        "/api/join-team",
        json={"team_code": "JOIN456"}
    )

    assert response.status_code == 401
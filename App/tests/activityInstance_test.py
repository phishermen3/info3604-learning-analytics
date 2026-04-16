import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from unittest.mock import patch, MagicMock

from App.views.activityInstance import instance_views


class MockUser:
    def __init__(self, id):
        self.id = id


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret-maximum-length-to-avoid-warnings"
    app.config["TESTING"] = True

    # Required for cookies JWT
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # disable for testing

    jwt = JWTManager(app)

    # Fix current_user
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        return MockUser(id=jwt_data["sub"])

    app.register_blueprint(instance_views)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_cookie(client, app):
    with app.app_context():
        token = create_access_token(identity="test_user")

    client.set_cookie(
        "access_token_cookie",
        value = token
    )

    return client

@patch("App.views.activityInstance.activity_controller")
def test_create_instance_success(mock_controller, auth_cookie):
    mock_instance = MagicMock()
    mock_instance.get_json.return_value = {"id": 1, "name": "Test Task"}

    mock_controller.create_activity_instance.return_value = mock_instance

    payload = {
        "activity_type": "quiz",
        "display_name": "Quiz 1",
        "course_id": "C1",
        "team_id": "T1",
        "project_id": "P1",
        "user_code": "U1"
    }

    response = auth_cookie.post("/api/instances", json=payload)

    assert response.status_code == 201
    assert response.get_json() == {"id": 1, "name": "Test Task"}

@patch("App.views.activityInstance.activity_controller")
def test_create_instance_default_display_name(mock_controller, auth_cookie):
    mock_instance = MagicMock()
    mock_instance.get_json.return_value = {"id": 2}

    mock_controller.create_activity_instance.return_value = mock_instance

    payload = {
        "activity_type": "assignment",
        "course_id": "C1",
        "team_id": "T1",
        "project_id": "P1",
        "user_code": "U1"
    }

    response = auth_cookie.post("/api/instances", json=payload)

    assert response.status_code == 201

    # Ensure default applied
    mock_controller.create_activity_instance.assert_called_with(
        "assignment",
        "New Task",  # 👈 important
        "C1",
        "T1",
        "P1",
        "U1"
    )

@patch("App.views.activityInstance.activity_controller")
def test_create_instance_value_error(mock_controller, auth_cookie):
    mock_controller.create_activity_instance.side_effect = ValueError("Invalid data")

    payload = {
        "activity_type": "quiz",
        "course_id": "C1",
        "team_id": "T1",
        "project_id": "P1",
        "user_code": "U1"
    }

    response = auth_cookie.post("/api/instances", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid data"}

@patch("App.views.activityInstance.activity_controller")
def test_get_instances_success(mock_controller, auth_cookie):
    mock_controller.get_activity_instances.return_value = [
        {"id": 1},
        {"id": 2}
    ]

    response = auth_cookie.get("/api/projects/P1/instances")

    assert response.status_code == 200
    assert response.get_json() == [{"id": 1}, {"id": 2}]

@patch("App.views.activityInstance.activity_controller")
def test_get_instances_value_error(mock_controller, auth_cookie):
    mock_controller.get_activity_instances.side_effect = ValueError("Invalid project")

    response = auth_cookie.get("/api/projects/P1/instances")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid project"}

@patch("App.views.activityInstance.activity_controller")
def test_get_instances_integration(mock_controller, auth_cookie):
    mock_controller.get_activity_instances.return_value = [{"id": 1}]

    response = auth_cookie.get("/api/projects/P1/instances")

    assert response.status_code == 200
    assert response.get_json() == [{"id": 1}]


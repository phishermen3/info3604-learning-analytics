import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from unittest.mock import patch, MagicMock

from App.views.courseEnrollment import courseEnrollment_views


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret-maximum-length-to-avoid-warnings"
    app.config["TESTING"] = True

    JWTManager(app)
    app.register_blueprint(courseEnrollment_views)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_header(app):
    with app.app_context():
        token = create_access_token(identity="test_user")
        return {"Authorization": f"Bearer {token}"}


def test_check_enrollment_missing_course_id(client, auth_header):
    response = client.post("/api/enrolled", headers=auth_header)

    assert response.status_code == 400
    assert response.get_json() == {"error": "course_id required"}

@patch("App.views.courseEnrollment.course_enrollment_controller")
def test_get_course_info_success(mock_controller, client, auth_header):
    mock_team = MagicMock(id=1)
    mock_project = MagicMock(id=10)

    mock_controller.get_course_info.return_value = (mock_team, mock_project)

    response = client.get(
        "/api/course-info?course_id=123",
        headers=auth_header
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "team_id": 1,
        "project_id": 10
    }


@patch("App.views.courseEnrollment.course_enrollment_controller")
def test_get_course_info_none(mock_controller, client, auth_header):
    mock_controller.get_course_info.return_value = (None, None)

    response = client.get(
        "/api/course-info?course_id=123",
        headers=auth_header
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "team_id": None,
        "project_id": None
    }

@patch("App.views.courseEnrollment.course_enrollment_controller")
def test_get_enrolled_courses_success(mock_controller, client, auth_header):
    mock_courses = [{"id": 1}, {"id": 2}]
    mock_controller.get_enrolled_courses.return_value = mock_courses

    response = client.get("/api/enrolled-courses", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json() == mock_courses


@patch("App.views.courseEnrollment.course_enrollment_controller")
def test_get_enrolled_courses_empty(mock_controller, client, auth_header):
    mock_controller.get_enrolled_courses.return_value = []

    response = client.get("/api/enrolled-courses", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json() == []


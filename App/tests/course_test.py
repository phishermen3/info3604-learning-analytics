from flask_jwt_extended import JWTManager
import pytest
from flask import Flask, app
from App.views.course import course_views

#PyTest fixture
@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "super-secret-test-key-maximum-length"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    jwt = JWTManager(app)
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_ACCESS_CSRF_HEADER_NAME"] = "X-CSRF-TOKEN"
    app.register_blueprint(course_views)
    with app.test_client() as client:
        yield client

def test_list_all_courses(client): 
    response = client.get("/courses")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert any(c["id"] == "COMP3608" for c in data)
    assert any(c["name"] == "Fundamentals of WAN Technology" for c in data)


def test_get_course_success(client):
    response = client.get("/courses/COMP3608")
    assert response.status_code == 200
    data = response.get_json()
    assert data["course id"] == "COMP3608"
    assert data["course name"] == "Intelligent Systems"


def test_get_course_not_found(client):
    response = client.get("/courses/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "Error: Course code invalid"
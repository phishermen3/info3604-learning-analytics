import pytest
from flask import Flask
from types import SimpleNamespace
from App.views.Course import course_bp, list_courses, get_course, courses 

#PyTest fixture
@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(course_bp)
    with app.test_client() as client:
        yield client

#Tests
def test_list_all_courses(client):
    list_courses.courses = [{"id": 123, "name": "Test Course"}]
    
    response = client.get("/courses")
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert any(c["id"] == 123 for c in data)


def test_get_course_success(client):
    get_course.courses = [{"id": 1, "name": "Math 101"}]
    
    response = client.get("/courses/1")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["course id"] == 1
    assert data["course name"] == "Math 101"


def test_get_course_not_found(client):
    get_course.courses = [{"id": 123, "name": "Test Course"}]
    
    response = client.get("/courses/9999")
    assert response.status_code == 401
    
    data = response.get_json()
    assert data["message"] == "Error: Course code invalid"
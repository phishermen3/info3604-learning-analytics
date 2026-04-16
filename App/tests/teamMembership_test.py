import pytest
from flask import Flask
from types import SimpleNamespace
from unittest.mock import patch

from App.views.teamMembership import teamMembership_views


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(teamMembership_views)

    with app.test_client() as client:
        yield client


def test_check_membership_no_auth(client):
    with patch("App.views.teamMembership.current_user", None):
        response = client.get("/courses/COMP3608/team1/membership")

        assert response.status_code == 500
        # route has no auth handling so None.id crashes


def test_check_membership_duplicate(client):
    fake_user = SimpleNamespace(
        id=1,
        enrolled_courses=[]
    )

    with patch("App.views.teamMembership.current_user", fake_user):
        with patch(
            "App.views.teamMembership.team_membership_controller.check_membership",
            return_value=True
        ):

            response = client.get("/courses/COMP3608/team1/membership")

            assert response.status_code == 409
            assert response.get_json()["error"] == "User already belongs to team"


def test_check_membership_not_duplicate_enrolled(client):
    fake_user = SimpleNamespace(
        id=1,
        enrolled_courses=[
            SimpleNamespace(id="COMP3608")
        ]
    )

    with patch("App.views.teamMembership.current_user", fake_user):
        with patch(
            "App.views.teamMembership.team_membership_controller.check_membership",
            return_value=False
        ):

            response = client.get("/courses/COMP3608/team1/membership")

            assert response.status_code == 200
            assert response.get_json()["enrolled"] is True


def test_check_membership_not_duplicate_not_enrolled(client):
    fake_user = SimpleNamespace(
        id=1,
        enrolled_courses=[
            SimpleNamespace(id="COMP2603")
        ]
    )

    with patch("App.views.teamMembership.current_user", fake_user):
        with patch(
            "App.views.teamMembership.team_membership_controller.check_membership",
            return_value=False
        ):

            response = client.get("/courses/COMP3608/team1/membership")

            assert response.status_code == 200
            assert response.get_json()["enrolled"] is False

@patch("App.views.teamMembership.team_membership_controller.check_membership")
def test_check_membership_multiple_courses_one_match(mock_check, client):
    # User is in two courses, only the second one matches the URL
    fake_user = SimpleNamespace(
        id=1,
        enrolled_courses=[
            SimpleNamespace(id="MATH1111"),
            SimpleNamespace(id="COMP3608")
        ]
    )
    mock_check.return_value = False

    with patch("App.views.teamMembership.current_user", fake_user):
        response = client.get("/courses/COMP3608/team1/membership")
        assert response.status_code == 200
        assert response.get_json()["enrolled"] is True

def test_check_membership_invalid_method(client):
    # This route only defines GET. Test that POST is blocked.
    response = client.post("/courses/COMP3608/team1/membership")
    assert response.status_code == 405

@patch("App.views.teamMembership.team_membership_controller.check_membership")
def test_check_membership_empty_enrollment(mock_check, client):
    # Test a user with a completely empty list
    fake_user = SimpleNamespace(id=1, enrolled_courses=[])
    mock_check.return_value = False

    with patch("App.views.teamMembership.current_user", fake_user):
        response = client.get("/courses/COMP3608/team1/membership")
        assert response.get_json()["enrolled"] is False
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


# ------------------------
# NO AUTH / INVALID USER
# ------------------------
def test_check_membership_no_auth(client):
    with patch("App.views.teamMembership.current_user", None):
        response = client.get("/courses/COMP3608/team1/membership")

        assert response.status_code == 500
        # route has no auth handling so None.id crashes


# ------------------------
# DUPLICATE MEMBERSHIP
# ------------------------
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


# ------------------------
# NOT DUPLICATE + ENROLLED
# ------------------------
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


# ------------------------
# NOT DUPLICATE + NOT ENROLLED
# ------------------------
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
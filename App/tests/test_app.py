from flask import app
from flask_jwt_extended import JWTManager
import os, tempfile, pytest, logging, unittest
from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash
from unittest.mock import patch

from App.main import create_app
from App.database import db, create_db
from App.models import User
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    create_log,
    get_logs
)


LOGGER = logging.getLogger(__name__)
#jwt = JWTManager(app)
'''
    Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("b000000b", "bobpass")
        assert user.user_code == "b000000b"

    def test_get_json(self):
        user = User("b000000b", "bobpass")
        if not user.created_at:
            user.created_at = datetime.now(timezone.utc)
        user_json = user.get_json()
        self.assertIn("id", user_json)
        self.assertEqual(user_json["user_code"], "b000000b")
        self.assertIn("created_at", user_json)
    
    def test_hashed_password(self):
        password = "bobpass"
        user = User("b000000b", password)
        assert getattr(user, "password_hash") != password

    def test_check_password(self):
        password = "bobpass"
        user = User("b000000b", password)
        assert user.check_password(password)
        
    def test_create_log(self):

        mock_registry = {
            "verbs": {
                "analyzed": {
                    "id": "https://logstack.azurewebsites.net/verbs/info3607/analyzed",
                    "display": {"en-US": "analyzed"}
                }
            },
            "activities": {
                "test-case": {
                    "objectType": "Activity",
                    "id": "https://logstack.azurewebsites.net/activity-types/info3607/test-case",
                    "definition": {
                        "name": {"en-US": "test case"}
                    }
                }
            },
            "stages": {"Analyze": {}},
            "problem_steps": {"Testing": {}}
        }

        with patch("App.controllers.log.load_course_registry") as mock_registry_loader, \
            patch("App.controllers.log.build_context") as mock_build_context:

            mock_registry_loader.return_value = mock_registry
            mock_build_context.return_value = {"contextActivities": {}}

            user = create_user("temp_user", "temppass")

            test_log, test_code = create_log(
                user_code=user.user_code,
                course_id=1,
                verb_name="analyzed",
                activity_name="test-case",
                team_id=1,
                project_id=1,
                pedagogical_stage="Analyze",
                problem_step="Testing",
                activity_instance_id="test-instance-123",
                display_name="Test Log Entry"
            )

            assert test_code == 201
            assert test_log["verb"]["display"]["en-US"] == "analyzed"
            assert test_log["actor"]["account"]["name"] == "temp_user"

            
        
'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db', 'SECRET_KEY': 'test-secret-key'})
    app.config["JWT_SECRET_KEY"] = "super-secret-test-key-maximum-length"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    jwt = JWTManager(app)
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_ACCESS_CSRF_HEADER_NAME"] = "X-CSRF-TOKEN"
    create_db()
    yield app.test_client()
    db.drop_all()


def test_authenticate():
    user = create_user("b000000b", "bobpass")
    access, refresh = login("b000000b", "bobpass", remember=False)
    assert access is not None


class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("LMNO1234", "rickpass")
        assert user.user_code == "LMNO1234"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertTrue(len(users_json) >= 1)
        for user in users_json:
            self.assertIn("id", user)
            self.assertIn("user_code", user)
            self.assertIn("created_at", user)
            
    # Tests retrieving statements from LRS
    def test_get_logs(self):
        user = create_user("newuser123", "supersecure")

        create_log(
            user_code=user.user_code,
            course_id=1,
            verb_name="analyzed",
            activity_name="test-case",
            team_id=1,
            project_id=1,
            pedagogical_stage="Analyze",
            problem_step="Testing",
            activity_instance_id="test-instance-123",
            display_name="Test Log Entry"
        )

        test_logs, test_code = get_logs(
            user_code=user.user_code,
            course_id=1,
            scope="course",
            team_code=1
        )

        assert test_code == 200

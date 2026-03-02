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
        test_verbs = {
            "analyzed": {
                "id": "https://yourdomain.com/verbs/analyzed",
                "display": { 
                    "en-US": "analyzed" 
                },
                "extensions": {
                    "https://yourdomain.com/xapi/extensions/pedagogical-stage": "Analyze"
                }
            }
        }
        
        test_activities = {
            "test-case": {
                "objectType": "Activity",
                "id": "https://yourapp/activity-types/test-case",
                "definition": {
                    "type": "https://yourapp/taxonomy/assessment",
                    "name": { "en-US": "Test Case" },
                    "description": { "en-US": "A test case created during project work" }
                }
            }
        }
        
        with patch("App.controllers.log.load_json") as mock_load:
            mock_load.side_effect = [test_verbs, test_activities]
        
        test_log, test_code = create_log("analyzed", "test-case")
        assert test_code == 201
        assert test_log["verb"]["display"]["en-US"] == "analyzed"
        
        
'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db', 'SECRET_KEY': 'test-secret-key'})
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
        test_logs, test_code = get_logs()
        assert test_code == 200

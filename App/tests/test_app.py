import os, tempfile, pytest, logging, unittest
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
    get_user_by_username,
    update_user,
    create_log,
    get_logs
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"

    # pure function no side effects or integrations called
    def test_get_json(self):
        user = User("bob", "bobpass")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id":None, "username":"bob"})
    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password)
        user = User("bob", password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
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
    user = create_user("bob", "bobpass")
    assert login("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("rick", "bobpass")
        assert user.username == "rick"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bob"}, {"id":2, "username":"rick"}], users_json)

    # Tests data changes in the database
    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
    
    # Tests retrieving statements from LRS
    def test_get_logs(self):
        test_logs, test_code = get_logs()
        assert test_code == 200


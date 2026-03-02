import os, tempfile, pytest, logging, unittest
from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user
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

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
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
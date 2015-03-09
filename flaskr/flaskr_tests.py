import os
import flaskr
import unittest
import tempfile


class FlaskrTestCase(unittest.TestCase):
    """
    Tests for Flaskr app
    """
    def setUp(self):
        self.db_fd, flaskr.app.config["DATABASE"] = tempfile.mkstemp()
        flaskr.app.config["TESTING"] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config["DATABASE"])

    def login(self, username, password):
        return self.app.post(
            "/login",
            data=dict(username=username, password=password),
            follow_redirects=True)

    def logout(self):
        return self.app.get("/logout", follow_redirects=True)

    def test_empty_db(self):
        """
        Test that correct message is set for non-existing records
        """
        # log in first
        lg = self.login("admin", "default")
        rv = self.app.get("/")
        self.logout()
        assert "No entries here so far" in rv.data

    def test_login_logout(self):
        """
        Test log in log out functionality
        """
        rv = self.login("admin", "default")
        assert "Logged in" in rv.data
        rv = self.logout()
        assert "Logged out" in rv.data
        rv = self.login("adminx", "default")
        assert "Invalid username" in rv.data
        rv = self.login("admin", "defaultx")
        assert "Invalid password" in rv.data

    def test_messages(self):
        self.login("admin", "default")
        rv = self.app.post(
            "/add",
            data=dict(
                title="<Hello>",
                content="<strong>HTML</strong> allowed here"),
            follow_redirects=True)
        assert "No entries here so far" not in rv.data
        assert "&lt;Hello&gt;" in rv.data
        assert "<strong>HTML</strong> allowed here"

if __name__ == "__main__":
    unittest.main()

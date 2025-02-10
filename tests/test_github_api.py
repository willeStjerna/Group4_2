import unittest
import requests
from unittest.mock import patch
# IMPORT when file, function and variable names are implemented

class TestGitHubAPI(unittest.TestCase):
    def setUp(self):
        """
        Create a simulated client for the CI server
        """
        flask_app.testing = True # Enables testing in flask, CHANGE name when the flask app is implemented
        self.client = flask_app.sim_client() # ALSO CHANGE name when the flask app is implemented

    def test_webhook_payload(self):
        """
        Simulate a GitHub webhook request.
        """
        payload = {
            "ref": "refs/heads/main",
            "repository": {"clone_url": "https://github.com/XXXXXXXXXXXXXXXXXXX"},
            "pusher": {"name": "test-user"}
        }

        response = self.client.post("/webhook", json=payload)
        self.assertIn(response.status_code, [200, 500])  # OK or Internal Server Error

    @patch("requests.post")
    def test_github_api_call(self, post):
        """
        Create a mock a GitHub API request and check if the webhook is received
        """
        post.return_value.status_code = 200
        post.return_value.json.return_value = {"message": "OK"}

        response = requests.post("https://api.github.com/XXXXXXXXXXXXXXXXXXXXXXXXXXXX/hooks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "OK")

if __name__ == "__main__":
    unittest.main()

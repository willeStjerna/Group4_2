import os
import sys
import unittest
from src.server import app

class ServerConnectionTest(unittest.TestCase):
    """
    Tests to ensure the minimal Flask server is responding and handling
    the /webhook endpoint as expected under various scenarios.
    These tests are only done locally and not online.
    """

    def setUp(self):
        """
        Configure the Flask test client before each test.
        """
        self.client = app.test_client()
        self.client.testing = True

    def test_root_endpoint_status_code(self):
        """
        Verify that GET / returns HTTP 200 OK.
        """
        response = self.client.get("/")
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected status 200, got {response.status_code}"
        )

    def test_root_endpoint_text_body(self):
        """
        Check that GET / returns the correct text or JSON message.
        """
        response = self.client.get("/")

        data = response.get_json()
        expected_message = "CI Server is running!"
        self.assertEqual(data.get("message"), expected_message, 
                         msg=f"Expected JSON 'message' to be {expected_message}")

    def test_webhook_post_correct(self):
        """
        Test that a correct POST request with JSON data to /webhook
        responds with status code 200 and contains the expected message.
        """

        test_payload = {
            "ref": "refs/heads/main",
            "repository": {
                "clone_url": "https://github.com/my_username/test_webhook.git",
            },

            "head_commit": {
                "id": "010bdeafe312d8d7b13a3263f6df25a815ffa41c",
                "message": "Update my_program.py",
                "url": "https://github.com/thier_username/test_webhook/commit/010bdeafe312d8d7b13a3263f6df25a815ffa41c",
                "author": {
                    "name": "Firstname Lastname",
                    "email": "36476090+my_username@users.noreply.github.com",
                    "username": "my_username"
                }
            }
        }

        response = self.client.post("/webhook", json=test_payload, content_type="application/json")

        # Status code check
        self.assertEqual(
            response.status_code,
            200,
            msg="Expected 200 when POSTing valid JSON, but got {}".format(response.status_code)
        )

    def test_webhook_post_no_data(self):
        """
        Test that a POST request to /webhook with no JSON data
        still responds with status code 200.
        """
        # No JSON data provided
        response = self.client.post("/webhook")

        # Should return 400 because its not allowed
        self.assertEqual(
            response.status_code,
            400,
            msg="Expected 400 when POSTing no data, but got {}".format(response.status_code)
        )

    def test_webhook_post_incorrect_content_type(self):
        """
        Test that sending a POST request to /webhook with an incorrect
        content-type (e.g., text/plain) is handled properly.
        """
        response = self.client.post(
            "/webhook",
            data="This is not JSON",
            content_type="text/plain"
        )

        # Should return 415 because its the wrong format 
        self.assertEqual(
            response.status_code,
            415,
            msg=f"Expected 415 for incorrect data type, got {response.status_code} when sending text/plain data."
        )

    def test_webhook_get_request(self):
        """
        Test that sending a GET request to the /webhook endpoint
        should typically return a 405 (Method Not Allowed) if only POST is defined.
        """
        response = self.client.get("/webhook")

        # By default, Flask returns a 405 if the route is only defined for POST.
        self.assertEqual(
            response.status_code,
            405,
            msg=f"Expected 405 for GET /webhook, but got {response.status_code}"
        )

    def test_404_for_unregistered_route(self):
        """
        Test that a request to an unregistered route returns a 404 (Not Found).
        """
        response = self.client.get("/some_nonexistent_route")

        self.assertEqual(
            response.status_code,
            404,
            msg=f"Expected 404 for an unregistered route, got {response.status_code}"
        )

    def test_webhook_post_invalid_json_syntax(self):
        """
        Test sending invalid JSON payload (malformed) to ensure the server
        either handles it gracefully or returns an error status.
        """
        # Malformed JSON (missing closing brace)
        malformed_json_data = '{"test": "hello"'
        response = self.client.post(
            "/webhook",
            data=malformed_json_data,
            content_type="application/json"
        )

        # Unsure what it will return but either 400 or 500
        expected_status = 400  # or possibly 500
        self.assertTrue(
            response.status_code in [400, 500],
            msg=f"Expected 400 or 500 when POSTing invalid JSON, got {response.status_code}"
        )


if __name__ == "__main__":
    unittest.main()

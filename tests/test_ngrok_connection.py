import os
import sys
import time
import unittest
import requests
import subprocess
from pyngrok import ngrok

NGROK_URL = "feasible-robin-vaguely.ngrok-free.app" 
PORT = 8004 

class TestNgrokIntegration(unittest.TestCase):
    """
    Example test suite that:
      1) Starts ngrok tunnel on port 8004 in setUpClass
      2) Tests connectivity to the public ngrok URL
      3) Shuts down ngrok in tearDownClass
    """

    @classmethod
    def setUpClass(cls):
        """Start the Flask server and the ngrok tunnel."""

        # Dynamically find the project root 
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..')
        )
        
        # Launch the Flask server with "-m src.server" so Python recognizes src/ as a package
        cls.server_process = subprocess.Popen(
            [sys.executable, "-m", "src.server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_root  # set working directory to the project root
        )

        cls.tunnel = ngrok.connect(
            addr=PORT,
            hostname=NGROK_URL,
        )

        cls.public_url = cls.tunnel.public_url

        # Give ngrok a moment to fully start up
        time.sleep(1)

    def test_get_root_endpoint(self):
        """
        Test that the root endpoint ('/') on the server is accessible
        via the public ngrok URL, returning status code 200.
        """
        url = f"{self.public_url}/"
        response = requests.get(url)
        self.assertEqual(
            response.status_code, 
            200, 
            f"Expected 200 OK from {url}, got {response.status_code}"
        )

        # If your server returns text like "CI Server is running!",
        # check it here:
        self.assertIn(
            "CI Server is running!",
            response.text,
            f"Expected 'CI Server is running!' in response, got {response.text}"
        )

    def test_post_webhook_endpoint(self):
        """
        Test that the server's '/webhook' endpoint is accessible via ngrok,
        receiving a JSON payload and returning a 200 with the expected response body.
        """
        url = f"{self.public_url}/webhook"
        payload = {"test": "ngrok-connection"}
        response = requests.post(url, json=payload)
        self.assertEqual(
            response.status_code, 
            200, 
            f"Expected 200 OK from {url}, got {response.status_code}"
        )
        
        self.assertIn(
            "Webhook received!",
            response.text,
            f"Expected 'Webhook received!' in response, got {response.text}"
        )

    @classmethod
    def tearDownClass(cls):
        """
        Stop servers after tests.
        """
        ngrok.kill()
        cls.server_process.terminate()

if __name__ == "__main__":
    unittest.main()
import os
import sys
import platform
import unittest
import requests
import subprocess
from pyngrok import ngrok


class TestNgrokIntegration(unittest.TestCase):
    """
    Example test suite that:
      1) Launch start_ngrok_server.py in a subprocess
      2) Tests connectivity to the public ngrok URL
      3) Shuts down ngrok in tearDownClass
    """
    def setUp(self):
        """Start the Flask server and the ngrok tunnel."""

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        start_ngrok_server_path = os.path.join(project_root, "src", "start_ngrok_server.py")

        self.server_process = None
        self.public_url = None

        try:
            self.server_process = subprocess.Popen(
                [sys.executable, start_ngrok_server_path],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Wait for the server to come online
            while True:
                line = self.server_process.stdout.readline()

                # If we didn't get a URL, raise an error
                if not line and self.server_process.poll() is not None:
                    raise RuntimeError("start_ngrok_server.py exited before providing a tunnel URL.")

                print(line, end="")

                # Look for a specific line that indicates the tunnel URL is established
                # Example: "ngrok tunnel established at: http://feasible-robin-vaguely.ngrok-free.app"
                if "ngrok tunnel established at:" in line:
                    parts = line.split("ngrok tunnel established at: ")
                    if len(parts) == 2:
                        self.public_url = parts[1].strip()
                        break

            if not self.public_url:
                raise RuntimeError("Failed to get the ngrok URL.")

        except Exception as e:
            if self.server_process:
                self.server_process.terminate()
            raise RuntimeError(f"Error during setUp: {str(e)}") from e

    def tearDown(self):
        """
        Stop servers after tests.
        """
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            ngrok.kill()

            os_name = platform.system()

            if os_name == "Windows":
                os.system("taskkill /F /IM ngrok.exe")
            elif os_name in ["Linux", "Darwin"]:  # Darwin == macOS
                subprocess.run(["pkill", "-f", "ngrok"], check=True)


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

        # Check we get a confirmation message
        self.assertIn(
            "CI Server is running!",
            response.text,
            f"Expected 'CI Server is running!' in response, got {response.text}"
        )


if __name__ == "__main__":
    unittest.main()

"""
CI Server Module

This module implements a Flask-based web server that handles GitHub webhooks
and manages the CI pipeline execution. It processes incoming webhook events,
triggers builds, and manages asynchronous CI operations.

Classes:
    CIServer: Manages CI workspace and build processes

Functions:
    index: Root endpoint that confirms server status
    webhook: Handles GitHub webhook POST requests
"""
import os
import uuid
from flask import Flask, request, jsonify
from git import Repo
import threading
import logging
from src.ci_pipeline import CIPipeline
from src.notifications import send_email_notification

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


members = {
    "agussarsson": "arvid.gussarsson@gmail.com",
    "andrelindgren": "andre.lindgren98@gmail.com",
    "willeStjerna": "wille.stjerna@gmail.com"
}

class CIServer:
    def __init__(self, base_dir='/tmp/ci_workspaces'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.pipeline = CIPipeline()
        
    def process_build(self, repo_url, branch_name, commit_id, author_email, author_username):
        """
        Executes the CI process: Clone repo, run syntax check, run tests, cleanup.
        """
        build_id = str(uuid.uuid4())
        workspace = os.path.join(self.base_dir, build_id)

        logging.info(f"Starting CI process for {repo_url} on branch {branch_name} (commit: {commit_id})")

        # Clone or pull the repository
        clone_success = self.pipeline.clone_pull_repo(repo_url, workspace, branch_name)
        if not clone_success:
            logging.error("Cloning repository failed.")
            send_email_notification(build_id, commit_id, author_email, "Failed", "Cloning repository failed.", author_username, branch_name)
            return build_id, False, "Cloning repository failed."

        # Run syntax check
        logging.info("Running syntax check...")
        syntax_output, syntax_success = self.pipeline.check_python_syntax(build_id, workspace)
        if not syntax_success:
            logging.error("Syntax errors detected.")
            return build_id, "failed", syntax_output

        # Run tests
        logging.info("Running tests...")
        std_output, tests_success = self.pipeline.run_tests(build_id, workspace)
        
        # Cleanup workspace
        logging.info("Cleaning up workspace...")
        self.pipeline.cleanup_workspace(workspace)

        # Determine final status
        final_status = "succeeded" if tests_success else "failed"
        logging.info(f"CI process completed with status: {final_status}")

        return build_id, final_status, std_output


# Flask API for CI Server
app = Flask(__name__)
ci_server = CIServer()

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "CI Server is running!"}), 200


# Handling GitHub webhooks
@app.route("/webhook", methods=["POST"])
def webhook():

    if request.content_type and request.content_type != "application/json":
        return jsonify({"error": "Unsupported Media Type, expected application/json"}), 415

    # Try to parse JSON 
    try:
        data = request.get_json(silent=True)  # silent=True prevents automatic 415 errors

        if not data:
            logging.error("400 No JSON data found")
            return jsonify({"error": "No JSON data found"}), 400

        # Handle ping from github
        if "zen" in data:
            logging.info("200: Github ping received, sending back pong")
            return jsonify({"msg": "pong"}), 200
        
        # Make sure its a push event
        if ("ref" not in data) or ("head_commit" not in data) or ("repository" not in data):
            logging.error("400 Not a push event")
            return jsonify({"error": "Not a valid push event"}), 400
        
        logging.info("Webhook received, processing data...")

        repo_url = data["repository"]["clone_url"]  # Extracted from top-level JSON
        branch_name = data["ref"].split("/")[-1]  # Extract branch name from "refs/heads/<branch>"
        commit_id = data["head_commit"]["id"]
        commit_message = data["head_commit"]["message"]
        commit_url = data["head_commit"]["url"]

        author_username = data["head_commit"]["author"]["username"]
        author_email = data["head_commit"]["author"]["email"]

        author_email = members.get(author_username)

        def run_ci(repo_url, branch_name, commit_id, author_email):
            """
            Function to execute CI process asynchronously.
            """
            logging.info(f"Starting async CI process for commit {commit_id} on branch {branch_name}...")
            build_id, test_success, log_output = ci_server.process_build(repo_url, branch_name, commit_id, author_email, author_username)
            send_email_notification(build_id, commit_id, author_email, test_success, log_output, author_username, branch_name)

        # Start a daemon thread
        thread = threading.Thread(target=run_ci, args=(repo_url, branch_name, commit_id, author_email))
        thread.daemon = True  # Ensures the thread does not block Flask shutdown
        thread.start()

        logging.info(f"CI process triggered for {commit_id} on branch {branch_name}")

        return jsonify({
            "message": "CI process started",
            "repository": repo_url,
            "branch": branch_name,
            "commit_id": commit_id,
            "commit_message": commit_message,
            "commit_url": commit_url
        }), 200

    except KeyError as e:
        logging.error(f"400 Missing expected data in webhook: {e}")
        return jsonify({"error": f"Missing expected data in webhook: {e}"}), 400

    except Exception as e:
        logging.error(f"500 Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error: {e}"}), 500


if __name__ == '__main__':
    logging.info("Starting CI Server...")
    app.run(port=8004, debug=True)  # port 8000 + <group number>
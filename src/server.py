# Flask server to handle GitHub webhooks
import os
import uuid
from flask import Flask, request, jsonify
from git import Repo
from .ci_pipeline import CIPipeline
from .notifications import send_email_notification
import threading

members = {
    "agussarsson": "arvid.gussarsson@gmail.com",
    "andrelindgren": "andrel4@kth.se",
    "willeStjerna": "wille.stjerna@gmail.com"
}

class CIServer:
    def __init__(self, base_dir='/tmp/ci_workspaces'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.pipeline = CIPipeline()
        
    def process_build(self, repo_url, branch_name, commit_id, author_email):
        """
        Executes the CI process: Clone repo, run syntax check, run tests, cleanup.
        """
        build_id = str(uuid.uuid4())
        workspace = os.path.join(self.base_dir, build_id)

        print(f"[CI SERVER] Starting CI process for {repo_url} on branch {branch_name} (commit: {commit_id})")

        # Clone or pull the repository
        clone_success = self.pipeline.clone_pull_repo(repo_url, workspace, branch_name)
        if not clone_success:
            send_email_notification(commit_id, author_email, "Failure", "Cloning repository failed.")
            return build_id, False, "Cloning repository failed."

        # Run syntax check
        syntax_success = self.pipeline.check_python_syntax(build_id, workspace)
        if not syntax_success:
            send_email_notification(commit_id, author_email, "Failure", "Syntax errors detected.")
            return build_id, False, "Syntax errors detected."

        # Run tests
        tests_success = self.pipeline.run_tests(build_id, workspace)
        
        # Cleanup workspace
        self.pipeline.cleanup_workspace(workspace)

        # Determine final status
        final_status = "Success" if tests_success else "Failure"
        send_email_notification(commit_id, author_email, final_status, "CI Process Completed.")

        return build_id, tests_success, "CI Process Completed."


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
            return jsonify({"error": "no JSON data found"}), 400

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
            build_id, test_success, log_output = ci_server.process_build(repo_url, branch_name, commit_id, author_email)
            send_email_notification(commit_id, author_email, "Success" if test_success else "Failure", log_output)

        # Start a daemon thread
        thread = threading.Thread(target=run_ci, args=(repo_url, branch_name, commit_id, author_email))
        thread.daemon = True  # Ensures the thread does not block Flask shutdown
        thread.start()
        return jsonify({
            "message": "CI process started",
            "repository": repo_url,
            "branch": branch_name,
            "commit_id": commit_id,
            "commit_message": commit_message,
            "commit_url": commit_url
        }), 200

    except KeyError as e:
        return jsonify({"error": f"Missing expected data in webhook: {e}"}), 400

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500


if __name__ == '__main__':
    app.run(port=8004, debug=True)  # port 8000 + <group number>
# Flask server to handle GitHub webhooks
import os
import uuid
from flask import Flask, request, jsonify
from git import Repo
from .ci_pipeline import CIPipeline
from .notifications import send_email_notification

members = {
    "agussarsson": "arvid.gussarsson@gmail.com"
}

class CIServer:
    def __init__(self, base_dir='/tmp/ci_workspaces'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.pipeline = CIPipeline()
        
    def process_build(self, repo_url):
        build_id = str(uuid.uuid4())
        workspace = os.path.join(self.base_dir, build_id)
        
        # Clone repository
        repo = Repo.clone_from(repo_url, workspace)
        
        # Run syntax check
        syntax_ok = self.pipeline.check_python_syntax(build_id, workspace)
        return build_id, syntax_ok


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

        print("data found:", data) # Print to let user know that data was found

        repo_url = data["repository"]["clone_url"]
        commit_id = data["head_commit"]["id"]
        author = data["pusher"]["name"]

        author_email = members.get(author)

        build_id, build_status, log_output = ci_server.process_build(repo_url)

        send_email_notification(commit_id, author_email, "Success" if build_status else "Failure", log_output) # Send automatic build email

        return jsonify({
            "build_id": build_id,
            "status": "Success" if build_status else "Failure",
            "logs": log_output
        }), 200

    except Exception:
        return jsonify({"error": "Invalid JSON format"}), 400


if __name__ == '__main__':
    app.run(port=8004, debug=True)  # port 8000 + <group number>
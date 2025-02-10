# Flask server to handle GitHub webhooks
import os
import uuid
from flask import Flask
from git import Repo
from .ci_pipeline import CIPipeline

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

if __name__ == '__main__':
    app.run(port=8004)  # port 8000 + <group number>
import os
import subprocess
import uuid
from flask import Flask, request, jsonify
from git import Repo

class CIServer:
    def __init__(self, base_dir='/tmp/ci_workspaces'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

# Flask API for CI Server
app = Flask(__name__)
ci_server = CIServer()

if __name__ == '__main__':
    app.run(port=8004)  # port 8000 + <group number>
"""
CI Pipeline Module

This module contains the main continuous integration logic including repository
management, syntax checking, and test execution functionality.

Classes:
    CIPipeline: Main CI logic (compilation, testing, syntax checking)
    
Functions:
    None (all functionality is encapsulated in the CIPipeline class)
"""
import ast
import os
import git
import subprocess
import shutil
import logging
from src.logger import BuildLogger


# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Use logging.DEBUG for more verbosity
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

class CIPipeline:
    def __init__(self):
        self.logger = BuildLogger()


    def clone_pull_repo(self, repo_url, repo_dir, branch_name="main"):
        """
        Clones or pulls a GitHub repository and checks out the correct branch.
        
        Args:
            repo_url (str): The Git repository URL.
            repo_dir (str): The directory where the repository should be cloned.
            branch_name (str): The branch to check out.
        
        Returns:
            bool: True if successful, False otherwise.
        """

        logging.info(f"Cloning repository: {repo_url} into {repo_dir} (branch: {branch_name})...")

        try:
            if os.path.exists(repo_dir):
                repo = git.Repo(repo_dir)
                repo.git.reset("--hard")
                repo.git.clean("-fd")
                repo.git.fetch()

                # Checkout the correct branch
                if branch_name in repo.heads:
                    repo.git.checkout(branch_name)
                else:
                    repo.git.checkout('-b', branch_name)

                repo.remotes.origin.pull()
                logging.info(f"Successfully pulled latest changes for branch {branch_name}.")
                self.logger.log_build_result(branch_name, "git", "success", f"Checked out and pulled branch {branch_name}.")
            else:
                git.Repo.clone_from(repo_url, repo_dir, branch=branch_name)
                self.logger.log_build_result(branch_name, "git", "success", f"Cloned repository at {repo_dir} with branch {branch_name}.")
                logging.info(f"Repository cloned successfully at {repo_dir}.")

            return True

        except Exception as e:
            self.logger.log_build_result(branch_name, "git", "failure", f"Error cloning/pulling repo: {e}")
            logging.error(f"Error cloning repository: {e}")
            return False
    
    def check_python_syntax(self, build_id, repo_path):
        """
        Perform static syntax checking on all Python files in a repo using the ast library.
        
        Args:
            build_id (str): Unique identifier for the build
            repo_path (str): Path to the repository
            
        Returns:
            bool: True if syntax check passes, False otherwise
        """
        
        logging.info(f"[Build {build_id}] Running Python syntax check...")
        syntax_errors = []
        
        # Walk through the repository and check .py files
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            source = f.read()
                        ast.parse(source, file_path)
                    except SyntaxError as e:
                        error_msg = f"Syntax error in {file_path}: {str(e)}"
                        syntax_errors.append(error_msg)
        
        # Log the results
        if syntax_errors:
            self.logger.log_build_result(
                build_id,
                'syntax_check',
                'failure',
                '\n'.join(syntax_errors)
            )
            logging.error(f"[Build {build_id}] Syntax check failed:\n" + "\n".join(syntax_errors))
            return syntax_errors, False
        
        self.logger.log_build_result(
            build_id,
            'syntax_check',
            'success',
            'All Python files passed syntax check'
        )
        logging.info(f"[Build {build_id}] Syntax check passed.")
        return "No syntax errors detected.", True
    
    def run_tests(self, build_id, repo_path):
        """
        Runs unit tests in the repository using pytest.
        
        Args:
            build_id (str): Unique identifier for the build.
            repo_path (str): Path to the repository.

        Returns:
            bool: True if all tests pass, False otherwise.
        """
        
        logging.info(f"[Build {build_id}] Running tests...")

        tests_dir = os.path.join(repo_path, "tests")

        # Check if a tests directory exists
        if not os.path.isdir(tests_dir):

            self.logger.log_build_result(build_id, "tests", "skipped", "No tests directory found.")
            logging.warning(f"[Build {build_id}] No tests directory found. Skipping tests.")

            return True  # No tests to run, treat as success

        try:
            # Run pytest and capture output
            result = subprocess.run(["pytest", tests_dir], capture_output=True, text=True)

            # Clean up the output from the tests
            lines = result.stdout.split("\n")
            cleaned = []
            skip_next = False

            for line in lines:
                if "test session starts" in line or "platform" in line or "rootdir" in line:
                    continue

                if "passed" in line or "failed" in line and "=" in line:
                    cleaned.append(line)
                    continue

                if line.strip() and not line.startswith("="):

                    if "tmp/ci_workspaces" in line or "C:\\tmp\\ci_workspaces" in line:
                        skip_next = True
                        continue

                    if "[" in line and "%" in line and "]" in line:
                        continue

                    if "self = " in line:
                        continue

                    if skip_next:
                        skip_next = False
                        continue

                    if "AssertionError" in line:
                        cleaned.append("Error cause: " + line)
                        continue

                    cleaned.append(line)

            cleaned_output = "\n".join(cleaned)

            if result.returncode == 0:

                self.logger.log_build_result(build_id, "tests", "success", "All tests passed.")
                logging.info(f"[Build {build_id}] All tests passed.")

                return "Build was successful", True
            else:

                self.logger.log_build_result(build_id, "tests", "failure", result.stdout + "\n" + result.stderr)
                logging.error(f"[Build {build_id}] Test failures:\n{result.stdout}\n{result.stderr}")
                
                return cleaned_output, False

        except Exception as e:

            self.logger.log_build_result(build_id, "tests", "failure", f"Test execution error: {e}")
            logging.error(f"[Build {build_id}] Error running tests: {e}")

            return cleaned_output, False
    
    def cleanup_workspace(self, repo_path):
        """
        Deletes the repository workspace after the CI process is complete.
        
        Args:
            repo_path (str): Path to the repository to be removed.
        """

        logging.info(f"Cleaning up workspace: {repo_path}...")

        try:

            shutil.rmtree(repo_path)
            self.logger.log_build_result("cleanup", "workspace", "success", f"Workspace {repo_path} removed.")
            logging.info(f"Workspace cleanup successful: {repo_path}.")

        except Exception as e:

            self.logger.log_build_result("cleanup", "workspace", "failure", f"Error deleting workspace: {e}")
            logging.error(f"Error during cleanup: {e}")




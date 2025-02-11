# Main CI logic (compilation, testing)
import ast
import os
from .logger import BuildLogger
import git
import subprocess

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
                self.logger.log_build_result(branch_name, "git", "success", f"Checked out and pulled branch {branch_name}.")
            else:
                git.Repo.clone_from(repo_url, repo_dir, branch=branch_name)
                self.logger.log_build_result(branch_name, "git", "success", f"Cloned repository at {repo_dir} with branch {branch_name}.")

            return True

        except Exception as e:
            self.logger.log_build_result(branch_name, "git", "failure", f"Error cloning/pulling repo: {e}")
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
            return False
        
        self.logger.log_build_result(
            build_id,
            'syntax_check',
            'success',
            'All Python files passed syntax check'
        )
        return True
    
    def run_tests(self, build_id, repo_path):
        
        tests_dir = os.path.join(repo_path, "tests")

        # Check if a tests directory exists
        if not os.path.isdir(tests_dir):
            self.logger.log_build_result(build_id, "tests", "skipped", "No tests directory found.")
            return True  # No tests to run, treat as success

        try:
            # Run pytest and capture output
            result = subprocess.run(["pytest", tests_dir], capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.log_build_result(build_id, "tests", "success", "All tests passed.")
                return True
            else:
                self.logger.log_build_result(build_id, "tests", "failure", result.stdout + "\n" + result.stderr)
                return False

        except Exception as e:
            self.logger.log_build_result(build_id, "tests", "failure", f"Test execution error: {e}")
            return False




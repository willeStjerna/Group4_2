# Main CI logic (compilation, testing)
import ast
import os
from .logger import BuildLogger
import git

class CIPipeline:
    def __init__(self):
        self.logger = BuildLogger()


    def clone_pull_repo(repo_url, repo_dir):
        """
        Function pulls or clones a GitHub repository based on a repo url. Pulls if repository already exists, otherwise clones.
        If the remote repo is pulled, it is reset to the latest commit (discarding local changes) and removes untracked directories.
        
        repo_url (str): The Git repository URL
        repo_dir (str): The directory to clone the repository
        """
        try:
            if os.path.exists(repo_dir):
                repo = git.Repo(repo_dir)
                repo.git.reset("--hard")
                repo.git.clean("-fd")
                repo.remotes.origin.pull()
                print("Repository was successfully pulled.")
            else:
                git.Repo.clone_from(repo_url, repo_dir)
                print("Repository was successfully cloned. Available at:", repo_dir)
            
        
        except Exception as e:
            print(f"An error occurred when cloning or pulling the remote repository: {e}")
    
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




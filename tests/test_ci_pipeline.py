import unittest
import os
import sys
import subprocess
import git
from unittest.mock import patch
# Update line below to match the file, function and variable names that are to be implemented
# from file_name import clone_pull_function, repo_url, repo_dir
repo_url = "https://github.com/willeStjerna/Group4_2"
repo_dir = "./test_repo"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import ci_pipeline

class TestCIPipeline(unittest.TestCase):

    @patch("git.Repo.clone_from")
    @patch("git.Repo.git.pull")
    def test_repo(self, mock_pull, mock_clone):
        """
        Test if the repository is cloned or pulled correctly.
        """
        if os.path.exists(repo_dir):
            ci_pipeline.clone_pull_repo(repo_url, repo_dir)
            mock_pull.assert_called()
        else:
            ci_pipeline.clone_pull_repo(repo_url, repo_dir)
            mock_clone.assert_called_with(repo_url, repo_dir)
            
            
    def test_check_python_syntax_valid(self):
        """
        Test syntax checking with valid Python code.
        """
        # Setup
        os.makedirs(self.test_repo_dir)
        test_file = os.path.join(self.test_repo_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def valid_function():\n    return True")

        # Execute
        result = self.pipeline.check_python_syntax(self.test_build_id, self.test_repo_dir)

        # Assert
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()

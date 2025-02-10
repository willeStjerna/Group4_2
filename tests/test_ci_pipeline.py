import unittest
import os
import subprocess
import git
from unittest.mock import patch
# Update line below to match the file, function and variable names that are to be implemented
# from file_name import clone_pull_function, repo_url, repo_dir

class TestCIPipeline(unittest.TestCase):

    @patch("git.Repo.clone_from")
    @patch("git.Repo.git.pull")
    def test_repo(self, mock_pull, mock_clone):
        """
        Test if the repository is cloned or pulled correctly.
        """
        if os.path.exists(repo_dir):
            # file_name.clone_pull_function(repo_url, repo_dir) TO BE CHANGED
            mock_pull.assert_called()
        else:
            # file_name.clone_pull_function(repo_url, repo_dir) TO BE CHANGED
            mock_clone.assert_called_with(repo_url, repo_dir)

if __name__ == "__main__":
    unittest.main()

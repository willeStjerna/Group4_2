import unittest
import os
import sys
import subprocess
import git
import shutil
from unittest.mock import patch
from src.ci_pipeline import CIPipeline

# Update line below to match the file, function and variable names that are to be implemented
# from file_name import clone_pull_function, repo_url, repo_dir
repo_url = "https://github.com/willeStjerna/Group4_2"

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestCIPipeline(unittest.TestCase):
    def setUp(self):
        """
        Set up test environment before each test.
        """
        self.pipeline = CIPipeline()
        self.test_build_id = "test_build"
        self.test_repo_dir = "./test_repo"

    def tearDown(self):
        """
        Clean up after each test.
        """
        if os.path.exists(self.test_repo_dir):
            shutil.rmtree(self.test_repo_dir)
    
    
    @patch("git.Repo")
    def test_clone_new_repository(self, mock_repo):
        """
        Test if the repository is cloned correctly when the directory doesn't exist.
        """
        mock_repo.clone_from.return_value = mock_repo
        
        result = self.pipeline.clone_pull_repo(repo_url, self.test_repo_dir)
        
        self.assertTrue(result)
        mock_repo.clone_from.assert_called_once_with(
            repo_url, 
            self.test_repo_dir, 
            branch="main"
        )

    @patch("git.Repo")
    def test_pull_existing_repository(self, mock_repo):
        """
        Test if the repository is pulled correctly when the directory exists.
        """
        os.makedirs(self.test_repo_dir)
        mock_repo.return_value.heads = ["main"]
        mock_instance = mock_repo.return_value
        
        result = self.pipeline.clone_pull_repo(repo_url, self.test_repo_dir)
        
        self.assertTrue(result)
        mock_repo.clone_from.assert_not_called()
        mock_instance.git.reset.assert_called_once_with("--hard")
        mock_instance.git.clean.assert_called_once_with("-fd")
        mock_instance.git.fetch.assert_called_once()
        mock_instance.remotes.origin.pull.assert_called_once()

    def test_check_python_syntax_valid(self):
        """
        Test syntax checking with valid Python code.
        """
        
        os.makedirs(self.test_repo_dir)
        test_file = os.path.join(self.test_repo_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def valid_function():\n    return True")

        result = self.pipeline.check_python_syntax(self.test_build_id, self.test_repo_dir)
        self.assertTrue(result)
        
    def test_check_python_syntax_invalid(self):
        """
        Test syntax checking with invalid Python code.
        """
        os.makedirs(self.test_repo_dir)
        test_file = os.path.join(self.test_repo_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("df invalid_function():\n    return True:")

        syntax_output, syntax_success = self.pipeline.check_python_syntax(self.test_build_id, self.test_repo_dir)
        self.assertFalse(syntax_success)
        
    @patch('subprocess.run')
    def test_run_tests_success(self, mock_run):
        """
        Test successful test execution with pytest.
        """
        os.makedirs(os.path.join(self.test_repo_dir, "tests"))
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "All tests passed"
        
        result = self.pipeline.run_tests(self.test_build_id, self.test_repo_dir)
        
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["pytest", os.path.join(self.test_repo_dir, "tests")],
            capture_output=True,
            text=True
        )
        
    def test_run_tests_no_test_directory(self):
        """
        Test behavior when no tests directory exists.
        """
        os.makedirs(self.test_repo_dir)  # No tests dir
        
        result = self.pipeline.run_tests(self.test_build_id, self.test_repo_dir)
        
        self.assertTrue(result)  # No tests = no tests to fail = True

        
    @patch('subprocess.run')
    def test_run_tests_failure(self, mock_run):
        """
        Test failed test execution with pytest.
        """
        os.makedirs(os.path.join(self.test_repo_dir, "tests"))
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "Test failures occurred"
        
        cleaned_output, success = self.pipeline.run_tests(self.test_build_id, self.test_repo_dir)
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()

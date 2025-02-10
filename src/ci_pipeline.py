# Main CI logic (compilation, testing)


import os
import git

def clone_pull_repo(repo_url, repo_dir):
    """
    Function pulls or clones a GitHub repository based on a repo url. Pulls if repository already exists, otherwise clones.
    
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

"""
Git integration for eGit using GitPython
"""
from typing import List, Optional, Tuple
from git import Repo, Git
from git.exc import GitCommandError
from pathlib import Path
from .config import load_config

def get_git_executable() -> str:
    """Get Git executable path from config"""
    config = load_config()
    return config.git_executable

def get_repo(path: Optional[Path] = None) -> Repo:
    """Get Git repository object"""
    try:
        return Repo(path or Path.cwd(), search_parent_directories=True)
    except Exception as e:
        raise Exception(f"Error accessing Git repository: {str(e)}")

def get_commit_messages(commit: str = "HEAD") -> str:
    """Get commit messages for a specific commit"""
    try:
        repo = get_repo()
        commit_obj = repo.commit(commit)
        return commit_obj.message
    except Exception as e:
        raise Exception(f"Error getting commit messages: {str(e)}")

def get_commit_diff(commit1: str, commit2: str) -> str:
    """Get diff between two commits"""
    try:
        repo = get_repo()
        diff = repo.git.diff(commit1, commit2)
        return diff
    except Exception as e:
        raise Exception(f"Error getting commit diff: {str(e)}")

def get_branch_commits(branch: Optional[str] = None) -> List[Tuple[str, str]]:
    """Get all commits on a branch"""
    try:
        repo = get_repo()
        if not branch:
            branch = repo.active_branch.name
        commits = list(repo.iter_commits(branch))
        return [(commit.hexsha, commit.message) for commit in commits]
    except Exception as e:
        raise Exception(f"Error getting branch commits: {str(e)}")

def execute_git_command(command: List[str]) -> str:
    """Execute a Git command"""
    try:
        git = Git(get_git_executable())
        return git.execute(command)
    except GitCommandError as e:
        raise Exception(f"Git command error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error executing Git command: {str(e)}")

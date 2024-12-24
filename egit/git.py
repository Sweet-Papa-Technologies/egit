"""Git operations for eGit."""

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

import git
from git import Repo
from git.exc import GitCommandError

from egit.config import settings


def get_repo(path: Optional[Path] = None) -> Repo:
    """Get Git repository at the specified path or current directory."""
    try:
        return Repo(path or Path.cwd(), search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        raise ValueError("Not a Git repository")


def get_diff(repo: Repo, commit_range: Optional[str] = None) -> str:
    """Get Git diff for the specified commit range."""
    try:
        if commit_range:
            return repo.git.diff(commit_range)
        else:
            return repo.git.diff("HEAD")
    except GitCommandError as e:
        raise ValueError(f"Failed to get diff: {e}")


def get_staged_changes(repo: Repo) -> str:
    """Get staged changes in the repository."""
    try:
        return repo.git.diff("--cached")
    except GitCommandError as e:
        raise ValueError(f"Failed to get staged changes: {e}")


def pass_through(args: List[str]) -> Tuple[int, str, str]:
    """Pass through Git command to system Git."""
    try:
        result = subprocess.run(
            [settings.git_executable, *args],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr

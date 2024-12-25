"""
Git operations module
"""
import subprocess
from typing import List, Optional
from pathlib import Path
from .config import get_config

def get_git_executable() -> str:
    """Get Git executable path from config"""
    config = get_config()
    return config.get("git_executable", "git")

def run_git_command(args: List[str], cwd: Optional[Path] = None) -> str:
    """Run a git command and return its output"""
    try:
        result = subprocess.run(
            [get_git_executable()] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if e.stderr:
            raise Exception(e.stderr.strip())
        raise e

def get_commit_message(commit: str) -> str:
    """Get the commit message for a given commit"""
    return run_git_command(["log", "--format=%B", "-n", "1", commit])

def get_commit_changes(commit: str) -> List[str]:
    """Get the list of changes in a commit"""
    output = run_git_command(["show", "--name-status", "--format=", commit])
    return [line.strip() for line in output.splitlines() if line.strip()]

def get_staged_changes() -> List[str]:
    """Get list of staged changes"""
    output = run_git_command(["diff", "--cached", "--name-status"])
    return [line.strip() for line in output.splitlines() if line.strip()]

def get_branch_changes() -> List[str]:
    """Get list of changes in current branch compared to main/master"""
    try:
        # First try to compare with main
        base_branch = "main"
        output = run_git_command(["diff", "--name-status", f"{base_branch}...HEAD"])
    except Exception:
        try:
            # If main doesn't exist, try master
            base_branch = "master"
            output = run_git_command(["diff", "--name-status", f"{base_branch}...HEAD"])
        except Exception:
            # If neither exists, show all changes in the current branch
            output = run_git_command(["diff", "--name-status", "HEAD"])
    
    return [line.strip() for line in output.splitlines() if line.strip()]

def get_current_branch() -> str:
    """Get the name of the current branch"""
    return run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])

def get_repo_root() -> Path:
    """Get the root directory of the git repository"""
    output = run_git_command(["rev-parse", "--show-toplevel"])
    return Path(output)

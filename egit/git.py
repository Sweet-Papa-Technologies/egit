"""
Git operations module
"""
import subprocess
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from .config import get_config

def get_git_executable() -> str:
    """Get Git executable path from config"""
    config = get_config()
    return config.get("git_executable", "git")

def run_git_command(args: List[str], cwd: Optional[Path] = None) -> str:
    """Run a git command and return its output"""
    try:
        # Start with current environment
        env = os.environ.copy()
        
        # Add encoding settings
        env.update({
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONUTF8": "1"
        })
        
        # Run command with UTF-8 encoding
        result = subprocess.run(
            [get_git_executable()] + args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
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

def get_commit_diff(commit: str) -> List[str]:
    """Get the full diff for a commit"""
    output = run_git_command(["show", "--patch", "--format=", commit])
    return output.splitlines()

def get_staged_changes() -> List[str]:
    """Get list of staged changes"""
    output = run_git_command(["diff", "--cached", "--name-status"])
    return [line.strip() for line in output.splitlines() if line.strip()]

def get_staged_diff() -> List[str]:
    """Get full diff of staged changes"""
    output = run_git_command(["diff", "--cached", "--patch"])
    return output.splitlines()

def get_branch_changes() -> List[str]:
    """Get list of changes in current branch compared to main/master"""
    try:
        # First try to compare with main
        base_branch = "main"
        output = run_git_command(["diff", "--name-status", f"{base_branch}..."])
    except Exception:
        try:
            # If main doesn't exist, try master
            base_branch = "master"
            output = run_git_command(["diff", "--name-status", f"{base_branch}..."])
        except Exception:
            # If neither exists, show all changes in the current branch
            output = run_git_command(["diff", "--name-status", "HEAD"])
    
    # Get any uncommitted changes as well
    try:
        staged_output = run_git_command(["diff", "--cached", "--name-status"])
        unstaged_output = run_git_command(["diff", "--name-status"])
        
        # Combine all changes, removing duplicates
        all_changes = set()
        for line in output.splitlines() + staged_output.splitlines() + unstaged_output.splitlines():
            if line.strip():
                all_changes.add(line.strip())
        
        return sorted(list(all_changes))
    except Exception:
        # If getting uncommitted changes fails, just return branch changes
        return [line.strip() for line in output.splitlines() if line.strip()]

def get_branch_diff() -> List[str]:
    """Get full diff of changes in current branch"""
    try:
        # First try to compare with main
        base_branch = "main"
        output = run_git_command(["diff", "--patch", f"{base_branch}..."])
    except Exception:
        try:
            # If main doesn't exist, try master
            base_branch = "master"
            output = run_git_command(["diff", "--patch", f"{base_branch}..."])
        except Exception:
            # If neither exists, show all changes in the current branch
            output = run_git_command(["diff", "--patch", "HEAD"])
    
    # Get any uncommitted changes as well
    try:
        staged_output = run_git_command(["diff", "--cached", "--patch"])
        unstaged_output = run_git_command(["diff", "--patch"])
        
        # Combine all diffs
        all_diffs = []
        all_diffs.extend(output.splitlines())
        all_diffs.extend(staged_output.splitlines())
        all_diffs.extend(unstaged_output.splitlines())
        
        return all_diffs
    except Exception:
        # If getting uncommitted changes fails, just return branch diff
        return output.splitlines()

def get_current_branch() -> str:
    """Get the name of the current branch"""
    return run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])

def get_repo_root() -> Path:
    """Get the root directory of the git repository"""
    output = run_git_command(["rev-parse", "--show-toplevel"])
    return Path(output)

def commit(message: str) -> None:
    """Create a new commit with the given message"""
    # Check if there are staged changes
    if not get_staged_changes():
        raise Exception("No changes staged for commit")
    run_git_command(["commit", "-m", message])

def get_last_tag() -> str:
    """Get the most recent tag"""
    return run_git_command(["describe", "--tags", "--abbrev=0"])

def get_root_commit() -> str:
    """Get the first commit in the repository"""
    return run_git_command(["rev-list", "--max-parents=0", "HEAD"])

def get_commits_between(from_ref: str, to_ref: str) -> List[Dict[str, Any]]:
    """Get all commits between two references"""
    output = run_git_command([
        "log",
        "--format=%H%n%s%n%b%n---%n",
        f"{from_ref}..{to_ref}"
    ])
    
    commits = []
    current_commit = {}
    
    for line in output.splitlines():
        if not line.strip():
            continue
        
        if line == "---":
            if current_commit:
                commits.append(current_commit)
                current_commit = {}
        elif not current_commit:
            current_commit = {"hash": line, "message": "", "body": []}
        elif "message" not in current_commit:
            current_commit["message"] = line
        else:
            current_commit["body"].append(line)
    
    # Add the last commit if there is one
    if current_commit:
        commits.append(current_commit)
    
    return commits

def has_uncommitted_changes() -> bool:
    """Check if there are any uncommitted changes (staged or unstaged)"""
    try:
        # Check both staged and unstaged changes
        run_git_command(["diff-index", "--quiet", "HEAD"])
        return False
    except subprocess.CalledProcessError:
        # Exit code 1 means there are uncommitted changes
        return True

def push_tag(tag: str) -> None:
    """Push a specific tag to the remote"""
    run_git_command(["push", "origin", tag])
    run_git_command(["push", "origin"])
    run_git_command(["fetch", "origin"])

def create_tag(tag: str, message: str) -> None:
    """Create an annotated tag with a message"""
    if has_uncommitted_changes():
        raise Exception("You have uncommitted changes. Please commit or stash them before creating a tag.")
    
    # Get the current HEAD commit
    head_commit = run_git_command(["rev-parse", "HEAD"])
    
    # Create tag on the current HEAD
    run_git_command(["tag", "-a", tag, head_commit, "-m", message])

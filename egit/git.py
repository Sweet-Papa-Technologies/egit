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
        output = run_git_command(["diff", "--name-status", "main..."])
    except Exception:
        try:
            output = run_git_command(["diff", "--name-status", "master..."])
        except Exception:
            output = run_git_command(["diff", "--name-status", "HEAD"])
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

# Internal helper to run git and return raw bytes (for binary detection)
def _run_git_command_bytes(args: List[str], cwd: Optional[Path] = None) -> bytes:
    """Run a git command and return raw bytes from stdout"""
    try:
        env = os.environ.copy()
        env.update({
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONUTF8": "1"
        })
        result = subprocess.run(
            [get_git_executable()] + args,
            capture_output=True,
            text=False,  # get bytes
            env=env,
            check=True,
            cwd=cwd
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        if e.stderr:
            # return empty bytes to indicate failure without raising
            return b""
        raise e

def get_diff_between(from_ref: str, to_ref: str, options: List[str] = None) -> str:
    """
    Get complete unified diff between two arbitrary Git references.
    """
    args = ["diff", "--patch", "-M", f"{from_ref}..{to_ref}"]
    if options:
        # Ensure options are before the ref range
        args = ["diff"] + options + ["--patch", "-M", f"{from_ref}..{to_ref}"]
    return run_git_command(args)

def get_changed_files_between(from_ref: str, to_ref: str) -> List[Dict[str, str]]:
    """
    Get list of all files changed between two references with status.
    Returns list of dicts: {'status': 'A/M/D/R', 'path': str, 'old_path': Optional[str]}
    """
    output = run_git_command(["diff", "--name-status", "-M", f"{from_ref}..{to_ref}"])
    changes: List[Dict[str, str]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split('\t')
        status = parts[0]
        # Normalize status to A/M/D/R; treat copies (C) as Added
        if status.startswith('R'):
            # Rename with score e.g., R100
            if len(parts) >= 3:
                changes.append({"status": "R", "path": parts[2], "old_path": parts[1]})
        elif status.startswith('C'):
            # Copy: treat as Added
            if len(parts) >= 3:
                changes.append({"status": "A", "path": parts[2], "old_path": parts[1]})
        else:
            if len(parts) >= 2:
                changes.append({"status": status, "path": parts[1], "old_path": None})
    return changes

def get_file_diff_between(from_ref: str, to_ref: str, filepath: str) -> str:
    """
    Get diff for a specific file between two references.
    """
    return run_git_command(["diff", "--patch", "-M", f"{from_ref}..{to_ref}", "--", filepath])

def get_diff_stats(from_ref: str, to_ref: str) -> Dict[str, Any]:
    """
    Get diff statistics (files changed, insertions, deletions) including per-file details.
    """
    import re
    short = run_git_command(["diff", "--shortstat", f"{from_ref}..{to_ref}"])
    files_changed = 0
    insertions = 0
    deletions = 0
    if short:
        # Example: "3 files changed, 25 insertions(+), 10 deletions(-)"
        m_files = re.search(r"(\d+)\s+files?\s+changed", short)
        m_ins = re.search(r"(\d+)\s+insertions?\(\+\)", short)
        m_del = re.search(r"(\d+)\s+deletions?\(-\)", short)
        files_changed = int(m_files.group(1)) if m_files else 0
        insertions = int(m_ins.group(1)) if m_ins else 0
        deletions = int(m_del.group(1)) if m_del else 0

    # Per-file stats
    numstat = run_git_command(["diff", "--numstat", "-M", f"{from_ref}..{to_ref}"])
    # Also get name-status for accurate status/renames
    name_status = run_git_command(["diff", "--name-status", "-M", f"{from_ref}..{to_ref}"])
    status_map: Dict[str, Dict[str, str]] = {}
    for line in name_status.splitlines():
        parts = line.split('\t')
        if not parts:
            continue
        s = parts[0]
        if s.startswith('R') and len(parts) >= 3:
            status_map[parts[2]] = {"status": "R", "old_path": parts[1]}
        elif s.startswith('C') and len(parts) >= 3:
            status_map[parts[2]] = {"status": "A", "old_path": parts[1]}
        elif len(parts) >= 2:
            status_map[parts[1]] = {"status": s, "old_path": None}

    details: List[Dict[str, Any]] = []
    seen_paths = set()
    for line in numstat.splitlines():
        # numstat line: added\tdeleted\tpath OR added\tdeleted\told\tnew for renames
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        added_str, deleted_str = parts[0], parts[1]
        # Binary files appear as '-' in numstat columns
        added = 0 if added_str == '-' else int(added_str or 0)
        deleted = 0 if deleted_str == '-' else int(deleted_str or 0)
        if len(parts) == 3:
            path = parts[2]
            old_path = status_map.get(path, {}).get("old_path")
            status = status_map.get(path, {}).get("status", "M")
        else:
            old_path = parts[2]
            path = parts[3]
            status = "R"
        details.append({
            "path": path,
            "old_path": old_path,
            "lines_added": added,
            "lines_removed": deleted,
            "status": status
        })
        seen_paths.add(path)

    # If shortstat didn't include files_changed (e.g., empty), fall back to unique count
    if files_changed == 0 and details:
        files_changed = len(seen_paths)

    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "details": details
    }

def is_binary_file(filepath: str, ref: Optional[str] = None) -> bool:
    """
    Check if a file is binary using git's detection/heuristics.
    """
    # First consult git attributes if present
    try:
        attr = run_git_command(["check-attr", "binary", "--", filepath])
        # Format: "<path>: binary: set" if marked binary
        if "binary: set" in attr:
            return True
    except Exception:
        # ignore if check-attr fails
        pass

    def is_binary_bytes(data: bytes) -> bool:
        if not data:
            return False
        # NUL byte is a strong indicator
        if b"\x00" in data:
            return True
        # Heuristic: ratio of non-text bytes
        textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x7F)))
        nontext = data.translate(None, textchars)
        return (len(nontext) / max(1, len(data))) > 0.30

    try:
        if ref:
            data = _run_git_command_bytes(["show", f"{ref}:{filepath}"])
            # If file doesn't exist at ref, treat as non-binary
            if data == b"":
                return False
            return is_binary_bytes(data[:4096])  # check first 4KB
        else:
            # Working tree
            p = Path(filepath)
            if not p.exists() or not p.is_file():
                return False
            with open(p, "rb") as f:
                chunk = f.read(4096)
                return is_binary_bytes(chunk)
    except Exception:
        return False

def get_file_content_at_ref(filepath: str, ref: str) -> Optional[str]:
    """
    Get the content of a file at a specific Git reference. Returns None for binary or missing files.
    """
    try:
        if is_binary_file(filepath, ref):
            return None
        return run_git_command(["show", f"{ref}:{filepath}"])
    except Exception:
        return None

def detect_subprojects(ref: str = "HEAD") -> List[Dict[str, str]]:
    """
    Detect subprojects/submodules and common dependency directories.
    """
    results: List[Dict[str, str]] = []

    # Detect submodules via .gitmodules
    gm = get_file_content_at_ref(".gitmodules", ref)
    if gm:
        for line in gm.splitlines():
            line = line.strip()
            if line.startswith("path ="):
                path = line.split("=", 1)[1].strip()
                results.append({"path": path, "type": "submodule"})

    # Scan tree for common dependency directories
    try:
        tree_names = run_git_command(["ls-tree", "-r", "--name-only", ref]).splitlines()
    except Exception:
        tree_names = []

    def add_if_present(prefix: str, typ: str):
        for name in tree_names:
            if name.startswith(prefix):
                results.append({"path": prefix.rstrip('/'), "type": typ})
                return

    add_if_present("node_modules/", "npm")
    add_if_present("Pods/", "pods")
    add_if_present("vendor/", "vendor")
    add_if_present("packages/", "monorepo")
    add_if_present("site-packages/", "python")
    add_if_present(".venv/", "python")

    # Deduplicate by path
    unique = {}
    for r in results:
        unique[r["path"]] = r["type"]
    return [{"path": p, "type": t} for p, t in unique.items()]

def normalize_ref_order(ref1: str, ref2: str) -> tuple[str, str]:
    """
    Ensure refs are in chronological order (oldest first, newest second).
    """
    try:
        t1 = int(run_git_command(["log", "-1", "--format=%ct", ref1]) or "0")
        t2 = int(run_git_command(["log", "-1", "--format=%ct", ref2]) or "0")
        if t1 <= t2:
            return (ref1, ref2)
        else:
            return (ref2, ref1)
    except Exception:
        # If timestamps cannot be resolved, keep original order
        return (ref1, ref2)

def resolve_ref(ref: str) -> Optional[str]:
    """
    Resolve a user-provided reference (short SHA, tag, branch, remote) to a commit hash.
    Returns None if it cannot be resolved.
    """
    if ref is None:
        return None
    ref = ref.strip()
    if not ref:
        return None

    # 1) Direct resolution
    try:
        return run_git_command(["rev-parse", "--verify", ref])
    except Exception:
        pass

    # 2) Dereference annotated tags to commit
    try:
        return run_git_command(["rev-parse", "--verify", f"{ref}^{{commit}}"])
    except Exception:
        pass

    # 3) Try explicit namespaces
    for candidate in (f"refs/heads/{ref}", f"refs/tags/{ref}", f"refs/remotes/origin/{ref}"):
        try:
            return run_git_command(["rev-parse", "--verify", candidate])
        except Exception:
            continue

    # 4) Fallback: search show-ref for matching names or short SHA prefixes
    try:
        output = run_git_command(["show-ref"])
        lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
        # Exact name match by the last path component
        matches = []
        for ln in lines:
            parts = ln.split()
            if len(parts) != 2:
                continue
            sha, name = parts
            last = name.rsplit("/", 1)[-1]
            if last == ref:
                matches.append((name, sha))

        # Prefer tags, then heads, then remotes
        def pick_prefix(pref: str) -> Optional[str]:
            for name, sha in matches:
                if name.startswith(pref):
                    return sha
            return None

        chosen = None
        for pref in ("refs/tags/", "refs/heads/", "refs/remotes/"):
            chosen = pick_prefix(pref)
            if chosen:
                break
        if not chosen and matches:
            chosen = matches[0][1]

        # If still not chosen, try short SHA prefix
        if not chosen:
            sha_candidates = []
            for ln in lines:
                parts = ln.split()
                if len(parts) == 2 and parts[0].startswith(ref):
                    sha_candidates.append(parts[0])
            if len(sha_candidates) == 1:
                chosen = sha_candidates[0]

        return chosen
    except Exception:
        return None

def fetch_all(remotes: bool = True, tags: bool = True, prune: bool = True) -> None:
    """
    Fetch updates from remote repositories so refs/tags are available locally.

    Args:
        remotes: If True, fetch all remotes (equivalent to '--all')
        tags: If True, fetch tags (equivalent to '--tags')
        prune: If True, prune deleted refs (equivalent to '--prune')

    Raises:
        Exception if fetch fails
    """
    args = ["fetch"]
    if remotes:
        args.append("--all")
    if tags:
        args.append("--tags")
    if prune:
        args.append("--prune")
    try:
        run_git_command(args)
    except Exception as e:
        raise Exception(f"Failed to fetch remotes: {str(e)}")

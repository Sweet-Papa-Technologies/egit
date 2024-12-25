"""
Tests for Git functionality
"""
import pytest
from egit import git
import subprocess

def test_get_staged_changes(mock_subprocess_run):
    """Test getting staged changes"""
    mock_subprocess_run.return_value.stdout = "M file1.py\nA file2.py"
    
    files = git.get_staged_changes()
    
    mock_subprocess_run.assert_called_once()
    assert isinstance(files, list)
    assert len(files) == 2

def test_get_staged_diff(mock_subprocess_run):
    """Test getting staged diff"""
    expected_diff = "+++ file1.py\n- old code\n+ new code"
    mock_subprocess_run.return_value.stdout = expected_diff
    
    diff = git.get_staged_diff()
    
    mock_subprocess_run.assert_called_once()
    assert isinstance(diff, list)  
    assert len(diff) == 3  

def test_get_branch_changes(mock_subprocess_run):
    """Test getting branch changes"""
    mock_subprocess_run.return_value.stdout = "M file1.py\nA file2.py"
    
    changes = git.get_branch_changes()
    
    mock_subprocess_run.assert_called_once()
    assert isinstance(changes, list)
    assert len(changes) == 2

def test_has_uncommitted_changes(mock_subprocess_run):
    """Test checking for uncommitted changes"""
    # Make subprocess.run raise CalledProcessError to simulate uncommitted changes
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "git diff-index")
    
    result = git.has_uncommitted_changes()
    
    mock_subprocess_run.assert_called_once()
    assert isinstance(result, bool)
    assert result is True

def test_create_tag(mock_subprocess_run):
    """Test creating a git tag"""
    git.create_tag("v1.0.0", "Release v1.0.0")
    
    mock_subprocess_run.assert_called()
    args = mock_subprocess_run.call_args[0][0]
    assert "tag" in args
    assert "v1.0.0" in args

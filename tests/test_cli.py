"""
Tests for CLI functionality
"""
import pytest
from typer.testing import CliRunner
from egit.cli import app

runner = CliRunner()

def test_version():
    """Test version command"""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "eGit version" in result.stdout

def test_config_show(mock_config, mocker):
    """Test showing configuration"""
    mocker.patch("egit.config.get_config", return_value=mock_config)
    
    result = runner.invoke(app, ["config", "--show"])
    
    assert result.exit_code == 0
    assert "Current Configuration" in result.stdout
    assert "llm_provider" in result.stdout

def test_config_set(mocker):
    """Test setting configuration"""
    mock_update = mocker.patch("egit.config.update_config")
    
    result = runner.invoke(app, ["config", "--set", "llm_model", "--value", "test-model"])
    
    assert result.exit_code == 0
    mock_update.assert_called_once_with("llm_model", "test-model")

def test_summarize(mock_config, mock_completion, mocker):
    """Test summarize command"""
    mocker.patch("egit.config.get_config", return_value=mock_config)
    mocker.patch("egit.git.get_staged_changes", return_value=["file1.py"])
    mocker.patch("egit.git.get_staged_diff", return_value="+ new code")
    mocker.patch("egit.llm.summarize_changes", return_value="Summary of changes")
    mocker.patch("egit.git.has_uncommitted_changes", return_value=True)
    
    result = runner.invoke(app, ["summarize"])
    
    assert result.exit_code == 0

def test_release_notes(mock_config, mock_completion, mocker):
    """Test release notes command"""
    mocker.patch("egit.config.get_config", return_value=mock_config)
    mocker.patch("egit.git.has_uncommitted_changes", return_value=False)
    mocker.patch("egit.git.get_commits_between", return_value=[
        {
            "hash": "abc123",
            "message": "feat: new feature",
            "author": "test@example.com",
            "date": "2024-01-01",
            "body": "Detailed description"
        }
    ])
    mocker.patch("egit.llm.generate_release_notes", return_value="Release notes content")
    mocker.patch("egit.git.get_last_tag", return_value="v0.1.0")
    
    result = runner.invoke(app, ["release-notes", "v1.0.0"])
    
    assert result.exit_code == 0

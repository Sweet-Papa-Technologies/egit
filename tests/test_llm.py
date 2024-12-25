"""
Tests for LLM functionality
"""
import pytest
import os
from typing import Dict, Any
from egit import llm
from unittest.mock import MagicMock, AsyncMock

def test_setup_llm_env(mock_config, mocker):
    """Test LLM environment setup"""
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    
    llm.setup_llm_env()
    
    assert os.environ.get("OPENAI_API_KEY") == "sk-123"
    assert os.environ.get("OPENAI_API_BASE") == "http://localhost:11434"

@pytest.mark.asyncio
async def test_get_llm_response(mock_config, mocker):
    """Test getting response from LLM"""
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    mock_completion = AsyncMock()
    mock_completion.return_value.choices = [
        MagicMock(message=MagicMock(content="Mocked LLM response"))
    ]
    mocker.patch("egit.llm.completion", mock_completion)
    
    response = await llm.get_llm_response("Test prompt")
    
    mock_completion.assert_called_once_with(
        model="ollama/llama3.2:3b",
        messages=[{"role": "user", "content": "Test prompt"}],
        temperature=0.7,
        max_tokens=4096,
        api_key="sk-123",
        api_base="http://localhost:11434"
    )
    assert isinstance(response, str)
    assert "Mocked LLM response" in response

def test_summarize_changes(mock_config, mocker):
    """Test summarizing code changes"""
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    mock_completion = MagicMock()
    mock_completion.return_value.choices = [
        MagicMock(message=MagicMock(content="Summary of changes"))
    ]
    mocker.patch("egit.llm.completion", mock_completion)
    
    changes = ["file1.py", "file2.py"]
    diffs = ["+ def test():", "- old code"]
    
    summary = llm.summarize_changes(changes, diffs)
    
    mock_completion.assert_called_once()
    assert isinstance(summary, str)
    assert "Summary of changes" in summary

def test_generate_release_notes(mock_config, mocker):
    """Test generating release notes"""
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    mock_completion = MagicMock()
    mock_completion.return_value.choices = [
        MagicMock(message=MagicMock(content="Release notes content"))
    ]
    mocker.patch("egit.llm.completion", mock_completion)
    
    commits = [
        {
            "hash": "abc123",
            "message": "feat: add new feature",
            "author": "test@example.com",
            "date": "2024-01-01",
            "body": "Detailed description"
        }
    ]
    
    notes = llm.generate_release_notes(commits, "v1.0.0")
    
    mock_completion.assert_called_once()
    assert isinstance(notes, str)
    assert "Release notes content" in notes

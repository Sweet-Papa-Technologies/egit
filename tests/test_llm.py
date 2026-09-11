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


# ---- regression tests: summary failures must never become commit messages ----

def _mock_response(text: str):
    resp = MagicMock()
    resp.choices = [MagicMock(message=MagicMock(content=text))]
    return resp


def test_summarize_changes_raises_on_llm_error(mock_config, mocker):
    """A provider error must raise, not be returned as the commit message"""
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    mocker.patch("egit.llm.completion", side_effect=Exception("API key not valid"))

    with pytest.raises(RuntimeError, match="Failed to generate summary"):
        llm.summarize_changes(["M file.py"], ["+x"])


def test_summarize_changes_raises_on_empty_response(mock_config, mocker):
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    mocker.patch("egit.llm.completion", return_value=_mock_response("   "))

    with pytest.raises(RuntimeError, match="empty"):
        llm.summarize_changes(["M file.py"], ["+x"])


def test_summarize_changes_retries_rate_limit(mock_config, mocker):
    """A 429 is retried using the provider's suggested delay, then succeeds"""
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    sleep = mocker.patch("egit.llm.time.sleep")
    rate_limited = Exception(
        'RateLimitError: code 429 RESOURCE_EXHAUSTED "retryDelay": "3s"'
    )
    completion = mocker.patch(
        "egit.llm.completion",
        side_effect=[rate_limited, _mock_response("Add retry handling")],
    )

    summary = llm.summarize_changes(["M file.py"], ["+x"])

    assert summary == "Add retry handling"
    assert completion.call_count == 2
    sleep.assert_called_once_with(4.0)  # provider delay + 1s


def test_summarize_changes_gives_up_after_repeated_rate_limits(mock_config, mocker):
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    mocker.patch("egit.llm.time.sleep")
    mocker.patch(
        "egit.llm.completion",
        side_effect=Exception("code 429 RESOURCE_EXHAUSTED"),
    )

    with pytest.raises(RuntimeError, match="Failed to generate summary"):
        llm.summarize_changes(["M file.py"], ["+x"])


def test_non_rate_limit_errors_are_not_retried(mock_config, mocker):
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    sleep = mocker.patch("egit.llm.time.sleep")
    completion = mocker.patch(
        "egit.llm.completion", side_effect=Exception("API key not valid")
    )

    with pytest.raises(RuntimeError):
        llm.summarize_changes(["M file.py"], ["+x"])

    assert completion.call_count == 1
    sleep.assert_not_called()


def test_summarize_changes_truncates_huge_diff(mock_config, mocker):
    """Oversized diffs are trimmed before being sent so quota is not blown"""
    mocker.patch("egit.llm.get_config", return_value=mock_config)
    completion = mocker.patch(
        "egit.llm.completion", return_value=_mock_response("Add lockfiles")
    )
    huge_diff = ["+" + ("x" * 1000)] * 400  # ~400k chars

    llm.summarize_changes(["A package-lock.json"], huge_diff)

    sent = completion.call_args.kwargs["messages"][1]["content"]
    assert len(sent) < llm.MAX_DIFF_CHARS + 2000
    assert "diff truncated" in sent


def test_truncate_diff_leaves_small_diffs_alone():
    assert llm._truncate_diff("small diff") == "small diff"

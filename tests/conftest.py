"""
Common test fixtures and configuration
"""
import pytest
from unittest.mock import MagicMock
from typing import Dict, Any

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock configuration for testing"""
    return {
        "llm_provider": "ollama",
        "llm_model": "ollama/llama3.2:3b",
        "llm_api_key": "sk-123",
        "llm_api_base": "http://localhost:11434",
        "llm_temperature": 0.7,
        "llm_max_tokens": 4096,
        "git_executable": "git"
    }

@pytest.fixture
def mock_completion(mocker):
    """Mock LiteLLM completion function"""
    mock = mocker.patch("litellm.completion")
    mock.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Mocked LLM response"
                }
            }
        ]
    }
    return mock

@pytest.fixture
def mock_subprocess_run(mocker):
    """Mock subprocess.run for git commands"""
    mock = mocker.patch("subprocess.run")
    mock.return_value = MagicMock(
        returncode=0,
        stdout="mocked git output",
        stderr="",
        text=True
    )
    return mock

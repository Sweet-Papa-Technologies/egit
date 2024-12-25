"""
Configuration management for eGit
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_FILE = "egit.json"

def get_config_dir() -> Path:
    """Get the configuration directory"""
    if os.name == 'nt':  # Windows
        config_dir = Path(os.environ.get('APPDATA', '')) / 'egit'
    else:  # Unix/Linux/macOS
        config_dir = Path.home() / '.config' / 'egit'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_config_path() -> Path:
    """Get the path to the config file"""
    return get_config_dir() / CONFIG_FILE

def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def get_config() -> Dict[str, Any]:
    """Get the current configuration, including environment variables"""
    config = load_config()
    
    # Environment variables take precedence
    env_vars = {
        "llm_provider": os.getenv("LLM_PROVIDER"),
        "llm_model": os.getenv("LLM_MODEL"),
        "llm_api_key": os.getenv("LLM_API_KEY"),
        "llm_api_base": os.getenv("LLM_API_BASE"),
        "llm_max_tokens": os.getenv("LLM_MAX_TOKENS"),
        "llm_temperature": os.getenv("LLM_TEMPERATURE"),
        "git_executable": os.getenv("GIT_EXECUTABLE")
    }
    
    # Update config with environment variables if they exist
    for key, value in env_vars.items():
        if value is not None:
            config[key] = value
    
    return config

def update_config(key: str, value: Any) -> None:
    """Update a configuration value"""
    config = load_config()
    config[key] = value
    save_config(config)

def get_config_value(key: str) -> Optional[Any]:
    """Get a specific configuration value"""
    config = get_config()
    return config.get(key)

# Default configuration
DEFAULT_CONFIG = {
    "llm_provider": "ollama",
    "llm_model": "ollama/llama3.2:3b",
    "llm_api_key": "sk-123",
    "llm_api_base": "http://localhost:11434",
    "llm_max_tokens": 4096,
    "llm_temperature": 0.7,
    "git_executable": "git"
}

# Initialize config with defaults if it doesn't exist
if not get_config_path().exists():
    save_config(DEFAULT_CONFIG)

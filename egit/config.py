"""
Configuration management for eGit
"""
from pathlib import Path
from typing import Optional, Dict, Any
import json
import os
from platformdirs import PlatformDirs
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Initialize platform-specific directories
dirs = PlatformDirs("egit", "egit")

# Define paths
CONFIG_DIR = Path(dirs.user_config_dir)
DATA_DIR = Path(dirs.user_data_dir)
CACHE_DIR = Path(dirs.user_cache_dir)
LOG_DIR = Path(dirs.user_log_dir)
ENV_FILE = CONFIG_DIR / ".env"
CONFIG_FILE = CONFIG_DIR / "egit.json"
DB_FILE = DATA_DIR / "egit.db"
LOG_FILE = LOG_DIR / "egit.log"

# Create necessary directories
for directory in [CONFIG_DIR, DATA_DIR, CACHE_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class EGitConfig(BaseModel):
    """eGit configuration model"""
    git_executable: str = Field(default="git")
    llm_provider: str = Field(default="ollama")
    llm_model: str = Field(default="openai/llama3.2:3b")
    llm_api_key: Optional[str] = Field(default=None)
    llm_api_base: str = Field(default="http://localhost:11434")
    llm_max_tokens: int = Field(default=4096)
    llm_temperature: float = Field(default=0.7)

def load_config() -> EGitConfig:
    """Load configuration from environment and config file"""
    # Load environment variables
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    
    # Load config file
    config_data: Dict[str, Any] = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
    
    # Environment variables take precedence over config file
    env_config = {
        "git_executable": os.getenv("GIT_EXECUTABLE", config_data.get("git_executable", "git")),
        "llm_provider": os.getenv("LLM_PROVIDER", config_data.get("llm_provider", "ollama")),
        "llm_model": os.getenv("LLM_MODEL", config_data.get("llm_model", "openai/llama3.2:3b")),
        "llm_api_key": os.getenv("LLM_API_KEY", config_data.get("llm_api_key")),
        "llm_api_base": os.getenv("LLM_API_BASE", config_data.get("llm_api_base", "http://localhost:11434")),
        "llm_max_tokens": int(os.getenv("LLM_MAX_TOKENS", config_data.get("llm_max_tokens", 4096))),
        "llm_temperature": float(os.getenv("LLM_TEMPERATURE", config_data.get("llm_temperature", 0.7))),
    }
    
    return EGitConfig(**env_config)

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to config file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def update_config(key: str, value: str) -> None:
    """Update a specific configuration value"""
    config_data = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
    
    config_data[key] = value
    save_config(config_data)

def get_config_value(key: str) -> Optional[str]:
    """Get a specific configuration value"""
    config = load_config()
    return getattr(config, key, None)

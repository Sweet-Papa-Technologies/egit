"""Configuration management for eGit."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    """LLM configuration settings."""
    provider: str = Field(default="ollama", description="LLM provider (ollama, openai, anthropic, vertex)")
    model: str = Field(default="llama3.2:3b", description="Model name to use")
    api_key: Optional[str] = Field(default=None, description="API key for the LLM service")
    api_base: Optional[str] = Field(default=None, description="Base URL for the LLM API")
    max_tokens: int = Field(default=4096, description="Maximum tokens for LLM response")
    temperature: float = Field(default=0.7, description="Temperature for LLM sampling")


class Settings(BaseSettings):
    """Global settings for eGit."""
    model_config = SettingsConfigDict(
        env_prefix="EGIT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # LLM Settings
    llm: LLMConfig = Field(default_factory=LLMConfig)
    
    # Docker Settings
    docker_image: str = Field(default="ollama/ollama", description="Docker image for Ollama")
    docker_container_name: str = Field(default="egit-ollama", description="Name for the Ollama container")
    
    # Git Settings
    git_executable: str = Field(default="git", description="Path to Git executable")
    
    # App Settings
    config_dir: Path = Field(
        default=Path.home() / ".egit",
        description="Directory for eGit configuration"
    )
    cache_dir: Path = Field(
        default=Path.home() / ".egit" / "cache",
        description="Directory for eGit cache"
    )
    debug: bool = Field(default=False, description="Enable debug mode")


def load_settings() -> Settings:
    """Load settings from environment variables and config file."""
    settings = Settings()
    
    # Ensure config directories exist
    settings.config_dir.mkdir(parents=True, exist_ok=True)
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    
    return settings


# Global settings instance
settings = load_settings()

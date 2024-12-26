# Configuration Guide

eGit can be configured through both environment variables and configuration files. This guide explains all available configuration options.

## Configuration Methods

1. **Configuration File**
   - Windows: `%APPDATA%\egit\egit.json`
   - Unix/Linux/macOS: `~/.config/egit/egit.json`

2. **Environment Variables**
   - Environment variables take precedence over config file settings

## Available Settings

### LLM Provider Settings

| Setting | Description | Default | Environment Variable |
|---------|-------------|---------|---------------------|
| `llm_provider` | LLM provider to use | `ollama` | `LLM_PROVIDER` |
| `llm_model` | Model name to use | `ollama/llama3.1:8b` | `LLM_MODEL` |
| `llm_api_key` | API key for the provider | `sk-123` | `LLM_API_KEY` |
| `llm_api_base` | API base URL | `http://localhost:11434` | `LLM_API_BASE` |
| `llm_max_tokens` | Maximum tokens for responses | `4096` | `LLM_MAX_TOKENS` |
| `llm_temperature` | Temperature for responses | `0.7` | `LLM_TEMPERATURE` |

### Git Settings

| Setting | Description | Default | Environment Variable |
|---------|-------------|---------|---------------------|
| `git_executable` | Path to Git executable | `git` | `GIT_EXECUTABLE` |

## Provider-Specific Configuration

### Ollama (Default)
```bash
egit config --set llm_provider --value ollama
egit config --set llm_api_base --value http://localhost:11434
egit config --set llm_model --value ollama/llama3.1:8b
egit config --set llm_api_key --value sk-123  # Dummy value required
```

### OpenAI
```bash
egit config --set llm_provider --value openai
egit config --set llm_api_base --value https://api.openai.com/v1
egit config --set llm_model --value gpt-4
egit config --set llm_api_key --value your_openai_key
```

### Anthropic
```bash
egit config --set llm_provider --value anthropic
egit config --set llm_api_base --value https://api.anthropic.com
egit config --set llm_model --value claude-2
egit config --set llm_api_key --value your_anthropic_key
```

### Google Gemini
```bash
egit config --set llm_provider --value google
egit config --set llm_api_key --value your_google_key
egit config --set llm_model --value gemini-pro
```

## Environment Variables Example
```bash
# Windows PowerShell
$env:LLM_PROVIDER = "openai"
$env:LLM_API_KEY = "your-api-key"

# Unix/Linux/macOS
export LLM_PROVIDER=openai
export LLM_API_KEY=your-api-key
```

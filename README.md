# eGit - Enhanced Git CLI with LLM Capabilities

eGit is a powerful CLI tool that enhances Git with LLM capabilities, making it easier to work with commit messages, generate release notes, and understand code changes.

## Features

- 🤖 Summarize commit changes using AI
- 📝 Generate comprehensive release notes
- 🔄 Compare and analyze differences between commits
- ⚙️ Flexible configuration for different LLM providers
- 💾 Caching system for faster responses
- 🔄 Git command passthrough for seamless integration

## Requirements

- Python 3.10 or higher
- Git
- One of the following LLM providers:
  - Ollama (default)
  - OpenAI
  - Anthropic
  - Google Vertex AI
  - LM Studio (OpenAI API Compatible)

## Installation

### Windows
```powershell
# Install Python 3.10 if not installed
choco install python310

# Install Git if not installed
choco install git

# Install eGit
python install.py
```

### macOS
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10 if not installed
brew install python@3.10

# Install Git if not installed
brew install git

# Install eGit
python3 install.py
```

### Linux (Debian/Ubuntu)
```bash
# Install Git if not installed
sudo apt-get install git

# Install Python 3.10 if not installed
# Download from https://www.python.org/downloads/release/python-31013/

# Install eGit
python3 install.py
```

## Configuration

eGit can be configured using environment variables or the config command:

```bash
# Set LLM provider
egit config llm_provider ollama

# Set model
egit config llm_model openai/llama3.2:3b

# Set API key (if needed)
egit config llm_api_key your_api_key

# View current configuration
egit config llm_provider
```

## Usage

### Summarize Latest Commit
```bash
egit summarize
```

### Summarize Specific Commit
```bash
egit summarize <commit-hash>
```

### Compare Two Commits
```bash
egit summarize-diff <commit1> <commit2>
```

### Generate Release Notes
```bash
egit release-notes [branch-name]
```

### Regular Git Commands
eGit passes through any unrecognized commands to Git, so you can use it as a drop-in replacement:
```bash
egit status
egit add .
egit commit -m "feat: add new feature"
```

### Version Information
Get the current version of eGit:
```bash
egit --version
# or
egit -v
```

## Environment Variables

- `GIT_EXECUTABLE`: Path to Git executable (default: system git)
- `LLM_PROVIDER`: LLM provider to use (default: ollama)
- `LLM_MODEL`: Model name (default: openai/llama3.2:3b)
- `LLM_API_KEY`: API key for the LLM service
- `LLM_API_BASE`: Base URL for the LLM API (default: http://localhost:11434)
- `LLM_MAX_TOKENS`: Maximum tokens for LLM response (default: 4096)
- `LLM_TEMPERATURE`: Temperature for LLM sampling (default: 0.7)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

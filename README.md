# eGit - Enhanced Git CLI with LLM Capabilities

eGit is a powerful CLI tool that enhances Git with LLM capabilities, making it easier to work with commit messages, generate release notes, and understand code changes.

## Features

- 🤖 AI-powered commit message generation from staged changes
- 📝 Intelligent release notes generation with automatic tagging
- 🔍 Smart change summarization for commits and branches
- ⚙️ Flexible configuration for different LLM providers
- 💾 Caching system for faster responses

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
# Download eGit
git clone https://github.com/Sweet-Papa-Technologies/egit.git
cd egit

# Run the installer
.\install.ps1
```

### macOS/Linux
```bash
# Download eGit
git clone https://github.com/Sweet-Papa-Technologies/egit.git
cd egit

# Make the installer executable
chmod +x install.sh

# Run the installer
./install.sh
```

The installer will:
1. Check for Python 3.10+ and Git
2. Create a virtual environment
3. Install required dependencies
4. Install eGit in development mode
5. Add eGit to your PATH (may require admin privileges on Windows)

### Manual PATH Configuration
If you don't have admin privileges on Windows, you can manually add eGit to your PATH:
1. Run the `setx` command shown during installation as administrator, or
2. Add the installation directory to your PATH environment variable

## Usage

NOTE: API KEY value must be set, otherwise LLM calls will fail. If your endpoint does not take an API key, please set a fake value such as `sk-123`. The value will be ignored if your endpoint does not need it.

### Summarize and Commit Changes
```bash
# View summary of staged changes
egit summarize --staged

# View summary of current branch changes
egit summarize --branch

# Generate summary and automatically commit staged changes
egit summarize --commit
```

### Generate Release Notes and Tags
```bash
# Generate release notes for version (draft mode)
egit release-notes 1.0.0 --draft

# Generate notes from specific range
egit release-notes 1.0.0 --from v0.9.0 --to main

# Create and push an annotated tag with release notes
egit release-notes 1.0.0 --tag
```

### Configuration Management
```bash
# View current configuration
egit config --show

# Set configuration values
egit config --set llm_provider ollama
egit config --set llm_model ollama/llama3.2:3b
egit config --set llm_api_key your_api_key
```

### Version Information
```bash
egit --version
# or
egit -v
```

## Environment Variables

- `GIT_EXECUTABLE`: Path to Git executable (default: system git)
- `LLM_PROVIDER`: LLM provider to use (default: ollama)
- `LLM_MODEL`: Model name (default: ollama/llama3.2:3b)
- `LLM_API_KEY`: API key for the LLM service (default: sk-123 for Ollama)
- `LLM_API_BASE`: Base URL for the LLM API (default: http://localhost:11434)
- `LLM_MAX_TOKENS`: Maximum tokens for LLM response (default: 4096)
- `LLM_TEMPERATURE`: Temperature for LLM sampling (default: 0.7)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

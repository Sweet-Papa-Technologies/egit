# eGit - Extended Git CLI with LLM Capabilities

eGit is a CLI tool that extends Git with LLM capabilities, making it easier to work with commit messages, generate release notes, and understand code changes.

## Features
- 🤖 AI-powered commit message generation from staged changes
- 📝 Intelligent release notes generation with automatic tagging
- 🔍 Smart change summarization for commits and branches
- ⚙️ Flexible configuration for different LLM providers

## Requirements
- macOS or Windows (Not tested on Linux, but should work and will be fully supported in the future)
- Python 3.10 or higher preinstalled
- Git preinstalled
- One of the following LLM providers:
  - Ollama (default)
  - LM Studio (Recommended for local models)
  - OpenAI
  - Anthropic
  - Google Gemini

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
1. Run the `setx` command shown during installation, or
2. Add the installation directory to your PATH environment variable

Alternatively, you can manually call eGit from the install directory:

```shell
# macOS or Linux
~/.egit/.venv/bin/egit

# Windows
C:\ProgramData\egit\.venv\Scripts\egit.exe
```

## Usage
NOTE: API KEY value must be set, otherwise LLM calls will fail. If your endpoint does not take an API key, please set a fake value such as `sk-123`. The value will be ignored if your endpoint does not need it.

#### How this would typically be used:
```bash
git add .
egit summarize --commit
git push
```

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

# Create and push an annotated tag with release notes
egit release-notes 1.0.0 --tag
```

### Configuration Management
```bash
# View current configuration
egit config --show

# Set configuration values
egit config --set llm_provider --value ollama
egit config --set llm_model --value ollama/llama3.2:3b
egit config --set llm_api_key --value your_api_key
```

### Version Information
```bash
egit --version
# or
egit -v
```

## Environment Variables
Settings can be set via Env Vars or via CLI flags. These are the available environment variables:

- `GIT_EXECUTABLE`: Path to Git executable (default: system git)
- `LLM_PROVIDER`: LLM provider to use (default: ollama)
- `LLM_MODEL`: Model name (default: ollama/llama3.2:3b)
- `LLM_API_KEY`: API key for the LLM service (default: sk-123 for Ollama)
- `LLM_API_BASE`: Base URL for the LLM API (default: http://localhost:11434)
- `LLM_MAX_TOKENS`: Maximum tokens for LLM response (default: 4096)
- `LLM_TEMPERATURE`: Temperature for LLM sampling (default: 0.7)

## Example LLM Provider Setup and Commands
Settings can be set via Env Vars or via CLI flags. These are the CLI Flags for each LLM Provider:

### Ollama
```bash
egit config --set llm_provider --value ollama
egit config --set llm_model --value ollama/llama3.2:3b
egit config --set llm_api_key --value sk-123
egit config --set llm_api_base --value http://localhost:11434
```

### LM Studio
```bash
egit config --set llm_provider --value lmstudio
egit config --set llm_model --value lm_studio/hermes-3-llama-3.1-8b
egit config --set llm_api_key --value sk-123
egit config --set llm_api_base --value http://localhost:1221/v1
```

### OpenAI
```bash
egit config --set llm_provider --value openai
egit config --set llm_model --value openai/gpt-4o
egit config --set llm_api_key --value myopenaiapikey
egit config --set llm_api_base --value https://api.openai.com/v1
```

### Anthropic
```bash
egit config --set llm_provider --value anthropic
egit config --set llm_model --value anthropic/claude-3-5-sonnet-20241022
egit config --set llm_api_key --value myanthropicapikey
egit config --set llm_api_base --value https://api.anthropic.com
egit config --set llm_max_tokens --value 8192 # NOTE: 8192 is the max for Anthropic
```

### Gemini
```bash
egit config --set llm_provider --value gemini
egit config --set llm_model --value gemini/gemini-1.5-pro
egit config --set llm_api_key --value mygeminiapikey
```

### Google Vertex AI
Not Supported yet (Coming Soon!)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

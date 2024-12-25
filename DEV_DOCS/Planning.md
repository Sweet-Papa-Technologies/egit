# eGit Planning and Requirements

## Requirements
- Will support both local and remote models (Ollama API, OpenAI Like API, Google Vertex, and Anthropic) via LiteLLM
- The app should be written in a clean and modualar way
- The app should use Typing to enforce type checking
- The app should use Pydantic to enforce data validation
- The app should use Pytest to test the code
- The app should use a requirements.txt file to install dependencies
- The app should check to see if all the required .env variables are set:
    - GIT_EXECUTABLE (Default to system git)
    - LLM_PROVIDER (Default to ollama)
    - LLM_MODEL (Default to openai/llama3.2:3b)
    - LLM_API_KEY (Default to None)
    - LLM_API_BASE (Default to http://localhost:11434)
    - LLM_MAX_TOKENS (Default to 4096)
    - LLM_TEMPERATURE (Default to 0.7)
- Functions to send inference to LLM
- User can set user configuration via command line or ENV variables
- Secrets will be stored in Env variables (ProgramData/egit/.env or ~/.egit/.env)
- The program itself wll be stored in a specific folder (ProgramData/egit/ or ~/.egit/)
- Will use a strong local model with a nice context window (At Least 32k tokens) llama3.2:3b
- Will pass any non-egit commands to Git
- Error handling for all functions, the app should be able to handle errors gracefully and provide clear and informative error messages
- Pretty output, especially for the installer script and the CLI itself (use emojis, colors, and animations)
- Will use ENV variables to configure LLM and user settings, save settings in a config file (ProgramData/egit/.env or ~/.egit/.env)
- Will use a config file to configure app settings (ProgramData/egit/egit.json or ~/.egit/egit.json)
- Will use a cache directory to store data (ProgramData/egit/cache or ~/.egit/cache)
- Will use a log file to store logs (ProgramData/egit/egit.log or ~/.egit/egit.log)
- Built in protections to prevent processing too much data
- Will use a venv to manage dependencies (ProgramData/egit/.venv or ~/.egit/.venv)
- Git commit messages should be output in plain text as a one liner, for easy parsing
- Release notes should be output in markdown format, for easy readability
- The app should save all generated messages and related git information to a SQLite database (ProgramData/egit/egit.db or ~/.egit/egit.db)
- Dedicated command and script for installing this application (a one-liner for Windows, Linux, and macOS). Includes robust error handling
    - Will check to see if Git is installed already
    - Will check to see if eGit is already installed, if so will do a git pull in the install directory to update source files
    - Will check to see if Python 3.10 is installed
    - Will add CLI commands to PATH

## Specificications
- App will be written in Python and will be a CLI app
- LiteLLM for LLM API management
- GitPython for Git API management

## CLI Commands

### Features
- `egit summarize <commit>` - Summarize commited changes using model
- `egit summarize-diff <commit1> <commit2>` - Show changes between two commits and summarize changes using model
- `egit release-notes <branch/commit>` - Generate release notes using model for all commits on specified branch or current branch if no branch is specified

### Configuration
- `egit config <key> <value>` - Set configuration value for eGit
- `egit config get <key>` - Get configuration value for eGit

#### Configuration Options
- `provider` - LLM provider (ollama, openai, anthropic, vertex)
- `model` - Model name to use
- `api_key` - API key for the LLM service
- `api_base` - Base URL for the LLM API
- `max_tokens` - Maximum tokens for LLM response
- `temperature` - Temperature for LLM sampling

## System Requirements
- 8 GB of RAM or Higher for local models (GPU or Apple Silicon recommended; Ollama or LM Studio)
- 4 GB of RAM or Higher for online models (OpenAI, Anthropic, Vertex)
- macOS, Linux (Debian or Ubuntu), or Windows
- Will assume user has Git installed
- Will assume user is either using:
    - Ollama API
    - LM Studio API (OpenAI API Compatible)
    - OpenAI API
    - Anthropic API
    - Google Vertex AI    

### Sumarize
```python
SUMMARY_PROMPT = f"""
You are a helpful assistant that summarizes GitLab commit messages. Please summarize all of the changes this person has made to their code based off the commit messages.
{context}
"""
```
## Useful Resources for Pre-Installation Requirements

### Package Managers:
- Chocolatey for Windows
    - Python Installer: `choco install python310`
    - Git Installer: `choco install git`
- Homebrew for macOS
    - Git Installer: `brew install git`
    - Python Installer: `brew install python@3.10`
- Apt for Linux (Debian or Ubuntu)
    - Git Installer: `sudo apt-get install git`
    - Python Installer: https://www.python.org/downloads/release/python-31013/ 

### Homebrew (macOS)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Chocolatey (Windows)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
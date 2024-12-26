# Getting Started with eGit

## Prerequisites
Before installing eGit, ensure you have:
- Python 3.10 or higher
- Git
- One of the supported LLM providers:
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

## Initial Setup

1. **Configure your LLM Provider**
   ```bash
   # Example for Ollama (default)
   egit config --set llm_provider --value ollama
   egit config --set llm_api_base --value http://localhost:11434
   egit config --set llm_model --value ollama/llama3.1:8b
   ```

2. **Set your API Key**
   ```bash
   # Required for all providers (use a dummy value like sk-123 for Ollama)
   egit config --set llm_api_key --value your_api_key_here
   ```

3. **Verify Installation**
   ```bash
   egit --version
   ```

## Next Steps
- Learn about [Basic Commands](basic-commands.md)
- Configure advanced settings in [Configuration](configuration.md)

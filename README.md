# eGit

A powerful AI-enhanced Git CLI tool that helps you manage your Git workflow with the power of LLMs. eGit seamlessly integrates with your existing Git commands while providing additional AI-powered features for commit message analysis and code change summaries.

## Features

- 🤖 AI-powered Git operations using local or cloud LLM models
- 📝 Automatic summarization of code changes
- 🔄 Seamless integration with existing Git workflow
- 🚀 Cross-platform support (Windows, macOS, Linux)
- 🎮 GPU acceleration support (NVIDIA, AMD)
- 🐳 Containerized LLM for easy deployment

## System Requirements

- **Operating System**: Windows, macOS, or Linux (Debian/Ubuntu)
- **Memory**:
  - 8GB+ RAM for local models
  - 4GB+ RAM for cloud models
- **Optional**:
  - NVIDIA GPU for accelerated inference
  - AMD GPU for accelerated inference
- **Dependencies** (automatically installed):
  - Python 3.10 or higher
  - Git
  - Docker
  - WSL2 (Windows only)

## Installation

### One-Line Installation

```bash
# Windows (PowerShell)
python -c "$(curl -fsSL https://raw.githubusercontent.com/Sweet-Papa-Technologies/egit/main/install.py)"

# macOS/Linux
python3 -c "$(curl -fsSL https://raw.githubusercontent.com/Sweet-Papa-Technologies/egit/main/install.py)"
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/Sweet-Papa-Technologies/egit.git
cd egit
```

2. Run the installer:
```bash
python install.py
```

The installer will:
- Install required system dependencies (Git, Python, Docker)
- Set up Docker and container runtime
- Install the eGit package
- Download and configure the LLM model

## Usage

eGit works as a drop-in replacement for Git. All standard Git commands work exactly the same:

```bash
# Standard Git commands work as normal
egit status
egit add .
egit commit -m "feat: add new feature"
egit push
```

### AI-Enhanced Commands

```bash
# Summarize staged changes
egit summarize

# Summarize changes between commits
egit summarize-diff HEAD~3 HEAD
```

## Configuration

eGit can be configured using environment variables or a config file located at `~/.egit/config.yaml`.

### Environment Variables

- `EGIT_LLM_PROVIDER`: LLM provider (default: "ollama")
- `EGIT_LLM_MODEL`: Model name (default: "llama3.2:3b")
- `EGIT_LLM_API_KEY`: API key for cloud providers
- `EGIT_LLM_API_BASE`: Custom API endpoint
- `EGIT_DEBUG`: Enable debug mode (true/false)

### Supported LLM Providers

- Ollama (local)
- OpenAI
- Anthropic
- Google Vertex AI

## Troubleshooting

### Common Issues

1. **Docker Issues**
   - Ensure Docker is running: `docker ps`
   - Restart Docker service if needed
   - For Windows, ensure WSL2 is properly installed

2. **Model Issues**
   - Check Ollama container logs: `docker logs egit-ollama`
   - Ensure enough disk space for model download
   - Verify network connection for model download

3. **Permission Issues**
   - Ensure user is in docker group
   - Run with elevated privileges if needed

### Getting Help

- Check the logs in `~/.egit/logs`
- Enable debug mode: `export EGIT_DEBUG=true`
- Open an issue on GitHub

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

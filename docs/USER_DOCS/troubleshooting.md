# Troubleshooting Guide

This guide helps you resolve common issues with eGit.

## Common Issues

### LLM Provider Issues

#### API Key Not Working
```
Error: Authentication failed
```

**Solutions:**
1. Check if your API key is set correctly:
   ```bash
   egit config --show
   ```
2. Try setting via environment variable:
   ```bash
   # Windows
   $env:LLM_API_KEY = "your-key"
   
   # Unix/Linux/macOS
   export LLM_API_KEY=your-key
   ```
3. For Ollama, any value (e.g., `sk-123`) works as API key is not used

#### Cannot Connect to LLM Provider
```
Error: Failed to connect to LLM provider
```

**Solutions:**
1. Check if the provider service is running
2. Verify API base URL:
   ```bash
   egit config --show
   ```
3. For Ollama, ensure the service is running:
   ```bash
   # Windows
   ollama serve
   
   # Unix/Linux/macOS
   sudo systemctl start ollama
   ```

### Git Integration Issues

#### Git Not Found
```
Error: Git executable not found
```

**Solutions:**
1. Ensure Git is installed and in PATH
2. Set Git executable path:
   ```bash
   egit config --set git_executable --value "C:\Program Files\Git\bin\git.exe"
   ```

#### Uncommitted Changes Error
```
Error: Please commit or stash your changes
```

**Solutions:**
1. Commit or stash changes:
   ```bash
   git add .
   egit summarize --commit
   # or
   git stash
   ```
2. Force operation (if applicable):
   ```bash
   git stash -u  # Stash including untracked files
   ```

### Release Notes Issues

#### Tag Already Exists
```
Error: Tag v1.0.0 already exists
```

**Solutions:**
1. Use a different version number
2. Delete existing tag (if appropriate):
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0  # If tag was pushed
   ```

#### No Changes Found
```
Error: No commits found in the specified range
```

**Solutions:**
1. Check if the commit range is valid:
   ```bash
   git log --oneline from_ref..to_ref
   ```
2. Ensure you have fetched all changes:
   ```bash
   git fetch --all --tags
   ```

## Performance Issues

### Slow Response Times

**Solutions:**
1. Use a local LLM provider like Ollama
2. Reduce max tokens:
   ```bash
   egit config --set llm_max_tokens --value 2048
   ```
3. Check network connection if using cloud providers

### High Memory Usage

**Solutions:**
1. Use a smaller model:
   ```bash
   egit config --set llm_model --value ollama/llama3.1:8b
   ```
2. Reduce batch size for large changes:
   - Make smaller, focused commits
   - Use specific file paths with `git add`

## Installation Issues

### Python Version Error
```
Error: Python 3.10 or higher required
```

**Solutions:**
1. Install Python 3.10+:
   ```bash
   # Windows
   winget install Python.Python.3.10
   
   # Unix/Linux/macOS
   brew install python@3.10  # macOS
   sudo apt install python3.10  # Ubuntu
   ```
2. Ensure Python is in PATH

### Virtual Environment Issues
```
Error: Failed to create virtual environment
```

**Solutions:**
1. Install virtualenv:
   ```bash
   pip install virtualenv
   ```
2. Clear existing virtual environment:
   ```bash
   rm -rf .venv/  # Unix/Linux/macOS
   rmdir /s /q .venv  # Windows
   ```
3. Manually create virtual environment:
   ```bash
   python -m venv .venv
   ```

## Getting Help

If you're still experiencing issues:

1. Check the version:
   ```bash
   egit --version
   ```

2. Enable debug logging:
   ```bash
   # Windows
   $env:DEBUG=1
   
   # Unix/Linux/macOS
   export DEBUG=1
   ```

3. File an issue on GitHub with:
   - eGit version
   - Operating system
   - Full error message
   - Steps to reproduce

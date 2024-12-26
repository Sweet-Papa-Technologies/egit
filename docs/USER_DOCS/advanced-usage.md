# Advanced Usage

This guide covers advanced features and usage patterns for eGit.

## Advanced Release Notes Generation

### Custom Release Note Ranges
You can generate release notes for specific commit ranges:

```bash
# From a specific tag to HEAD
egit release-notes v1.1.0 --from v1.0.0

# Between two specific references
egit release-notes v2.0.0 --from release/1.9 --to feature/new-api

# From the first commit
egit release-notes v1.0.0 --from $(git rev-list --max-parents=0 HEAD)
```

### Draft Release Notes
Generate draft release notes to preview before creating a tag:

```bash
# Preview release notes
egit release-notes v1.1.0 --draft

# Review and then create the actual release
egit release-notes v1.1.0 --tag
```

## Advanced Change Summarization

### Comparing Specific References
```bash
# Summarize changes between branches
egit summarize origin/main...feature/new-feature

# Summarize specific commit
egit summarize abc123

# Summarize range of commits
egit summarize main~5..main
```

### Auto-Commit with Custom Options
```bash
# Stage all changes and commit
git add .
egit summarize --commit

# Stage specific files and commit
git add src/specific-file.js
egit summarize --commit
```

## Working with Different LLM Providers

### Switching Providers Temporarily
You can temporarily switch providers using environment variables:

```bash
# Windows PowerShell
$env:LLM_PROVIDER = "openai"
$env:LLM_API_KEY = "your-key"
egit summarize --staged

# Unix/Linux/macOS
LLM_PROVIDER=openai LLM_API_KEY=your-key egit summarize --staged
```

### Provider-Specific Features
Different providers may have different capabilities:

- **Ollama**: Best for local development, no API key needed
- **OpenAI**: Best quality for complex changes
- **Anthropic**: Good for detailed analysis
- **Google Gemini**: Balanced performance

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Release Notes
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0
      
      - name: Generate Release Notes
        env:
          LLM_PROVIDER: openai
          LLM_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          # Install eGit
          python -m pip install egit
          
          # Generate release notes
          egit release-notes ${{ github.ref_name }} --from $(git describe --tags --abbrev=0 HEAD^) --tag
```

## Best Practices

1. **Commit Messages**
   - Stage related changes together for better summaries
   - Review auto-generated messages before committing

2. **Release Notes**
   - Use `--draft` to preview before creating tags
   - Keep version numbers consistent with semver

3. **Configuration**
   - Use environment variables in CI/CD
   - Use config file for local development

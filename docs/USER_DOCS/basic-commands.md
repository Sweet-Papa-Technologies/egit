# Basic Commands

eGit provides several powerful commands to enhance your Git workflow. Here are the main commands you'll use:

## Summarize Changes

### View Staged Changes
```bash
egit summarize --staged
```
This shows a natural language summary of your staged changes.

### View Branch Changes
```bash
egit summarize --branch
```
Shows changes in your current branch compared to the main branch.

### Auto-Commit with Summary
```bash
egit summarize --commit
```
Generates a commit message and automatically commits staged changes.

### Summarize Specific Commit
```bash
egit summarize abc123  # Replace abc123 with commit hash
```

## Generate Release Notes

### Create Release Notes
```bash
egit release-notes v1.0.0
```
Generates release notes for version v1.0.0.

### Draft Release Notes
```bash
egit release-notes v1.0.0 --draft
```
Preview release notes without creating a tag.

### Create Tagged Release
```bash
egit release-notes v1.0.0 --tag
```
Generates release notes and creates a Git tag.

### Custom Range Release Notes
```bash
egit release-notes v1.0.0 --from v0.9.0 --to HEAD
```
Generate notes for changes between v0.9.0 and HEAD.

## Configuration

### View Current Config
```bash
egit config --show
```

### Set Configuration Value
```bash
egit config --set key_name --value value
```

## Common Workflows

### Typical Commit Workflow
```bash
git add .
egit summarize --commit
git push
```

### Release Workflow
```bash
# Create release notes and tag (tag will be pushed to remote)
egit release-notes v1.0.0 --tag
```

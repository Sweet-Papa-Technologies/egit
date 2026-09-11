# eGit in Docker

Run eGit without installing Python or dependencies on your host. Build the image once, then mount any Git repo and run commands inside the container.

## Build
From the repo root (where the Dockerfile lives)
```bash
docker build -t egit .
```

## Run

Mount your Git repository and set the working directory to that mount so eGit can see the .git folder.

### Show help
```bash
docker run --rm egit
```
### Summarize staged changes
```bash
docker run --rm \
-e LLM_PROVIDER=ollama \
-e LLM_MODEL=ollama/llama3.2:3b \
-e LLM_API_BASE=http://host.docker.internal:11434 \ 
-e LLM_API_KEY=sk-123 \ 
-v "$(pwd)":/work -w /work egit summarize --staged
```
### Create a commit with AI summary
```bash
docker run --rm \
-e LLM_PROVIDER=ollama \
-e LLM_MODEL=ollama/llama3.2:3b \
-e LLM_API_BASE=http://host.docker.internal:11434 \ 
-e LLM_API_KEY=sk-123 \ 
-v "$(pwd)":/work -w /work egit summarize --commit
```


## Troubleshooting

- “exec: 'egit': not found”
  - Ensure your image installs eGit onto PATH or set ENTRYPOINT to the installed binary. If you used a venv, add it to PATH (e.g., `ENV PATH="/root/.egit/.venv/bin:${PATH}"`).

- “git does not know --cached”
  - Confirm you’re inside a repo: mount includes `.git` and `-w /work` points to it.

- Git help triggers man error during build
  - Use `git diff -h` instead of `git diff --help` in Dockerfile checks.

That’s it—build once, mount any repo, and run eGit commands inside Docker.
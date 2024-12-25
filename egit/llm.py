"""
LLM integration for eGit using LiteLLM
"""
from typing import Optional, List, Dict, Any
from litellm import completion
from .config import load_config, get_config
import os

SUMMARY_PROMPT = """
You are a helpful assistant that summarizes GitLab commit messages. Please summarize all of the changes this person has made to their code based off the commit messages.
{context}
"""

RELEASE_NOTES_PROMPT = """
You are a helpful assistant that generates release notes from Git commit messages. Please generate clear and organized release notes in markdown format based on the following commit messages:
{context}
"""

def setup_llm_env():
    """Setup LLM environment variables based on configuration"""
    config = get_config()
    
    # Set environment variables for Ollama
    if config.get("llm_provider") == "ollama":
        os.environ["OPENAI_API_KEY"] = "sk-123"  # Ollama needs any non-empty key
        os.environ["OPENAI_API_BASE"] = config.get("llm_api_base", "http://localhost:11434/v1")
    else:
        # For other providers, use the configured values
        if config.get("llm_api_key"):
            os.environ["OPENAI_API_KEY"] = config["llm_api_key"]
        if config.get("llm_api_base"):
            os.environ["OPENAI_API_BASE"] = config["llm_api_base"]

async def get_llm_response(prompt: str, max_tokens: Optional[int] = None) -> str:
    """Get response from LLM"""
    config = get_config()
    setup_llm_env()
    
    try:
        model = config.get("llm_model", "ollama/llama3.2:3b")
        if config.get("llm_provider") == "ollama":
            # Strip 'openai/' prefix for Ollama models
            model = model.replace("openai/", "ollama/")
            
        response = await completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=float(config.get("llm_temperature", 0.7)),
            max_tokens=int(max_tokens or config.get("llm_max_tokens", 4096)),
            api_key=config.get("llm_api_key", "sk-123"),
            api_base=config.get("llm_api_base", "http://localhost:11434")
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error getting LLM response: {str(e)}")

async def summarize_commits(commit_messages: str) -> str:
    """Summarize commit messages using LLM"""
    prompt = SUMMARY_PROMPT.format(context=commit_messages)
    return await get_llm_response(prompt)

# async def generate_release_notes(commit_messages: str) -> str:
#     """Generate release notes from commit messages using LLM"""
#     prompt = RELEASE_NOTES_PROMPT.format(context=commit_messages)
#     return await get_llm_response(prompt)

def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration"""
    config = get_config()
    setup_llm_env()
    model = config.get("llm_model", "ollama/llama3.2:3b")
    if config.get("llm_provider") == "ollama":
        # Strip 'openai/' prefix for Ollama models
        model = model.replace("openai/", "ollama/")
    return {
        "model": model,
        "api_base": config.get("llm_api_base", "http://localhost:11434"),
        "api_key": config.get("llm_api_key", "sk-123"),
        "max_tokens": int(config.get("llm_max_tokens", "500")),
        "temperature": float(config.get("llm_temperature", "0.7")),
    }

def summarize_changes(changes: List[str], diffs: List[str]) -> str:
    """Generate a natural language summary of the changes"""
    config = get_config()
    
    # Setup environment variables
    setup_llm_env()
    
    # Prepare the prompt with both file changes and diffs
    changes_text = "\n".join(changes)
    diff_text = "\n".join(diffs)
    
    prompt = f"""Please summarize these Git changes in a clear, concise way:

File Changes:
{changes_text}

Detailed Changes:
{diff_text}

Focus on:
1. The main types of changes (added, modified, deleted files)
2. Key components or areas that were changed
3. Specific code changes and their purpose
4. Any patterns in the changes

Keep the summary brief but informative.
ENSURE the summary is a single paragraph, on a single line.
Make the summary suitable for a commit message.

ONLY respond with the summary, nothing else.
"""

    # Get response from LLM
    try:
        model = config.get("llm_model", "ollama/llama3.2:3b")
        if config.get("llm_provider") == "ollama":
            # Strip 'openai/' prefix for Ollama models
            model = model.replace("openai/", "ollama/")
            
        response = completion(
            model=model,
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant that summarizes Git changes in a clear, concise way. Focus on the specific code changes and their purpose."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=float(config.get("llm_temperature", 0.7)),
            max_tokens=int(config.get("llm_max_tokens", 4096)),
            api_key=config.get("llm_api_key", "sk-123"),
            api_base=config.get("llm_api_base", "http://localhost:11434")
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_release_notes(commits: List[Dict[str, Any]], version: str) -> str:
    """Generate release notes from a list of commits"""
    llm_config = get_llm_config()
    
    # Format commits for the prompt
    commit_list = []
    for commit in commits:
        commit_text = f"Commit: {commit['hash']}\n"
        commit_text += f"Message: {commit['message']}\n"
        if commit['body']:
            commit_text += f"Details: {' '.join(commit['body'])}"
        commit_list.append(commit_text)
    
    # Create the prompt
    prompt = f"""Generate a very concise release note for version {version} suitable for a git tag message.

Commits:
{chr(10).join(commit_list)}

Requirements:
1. First line must be a clear, complete summary (this is what GitHub shows in the UI)
2. Use this exact format:
   <clear complete summary that can stand alone>
   
   FEATURES:
   - <feature>
   - <feature>
   
   FIXES:
   - <fix>
   
   CHANGES:
   - <change>

3. Keep it extremely brief - each bullet should be one line
4. No markdown, no formatting, just plain text
5. No placeholders, only include sections that have actual changes
6. The first line must make sense on its own as it will be shown separately

ONLY respond with the release notes in the exact format above. Keep it very concise."""

    # Call the LLM
    response = completion(
        messages=[{
            "role": "system",
            "content": "You are an expert at writing clear, concise release notes for git tags that display well on GitHub."
        }, {
            "role": "user",
            "content": prompt
        }],
        **llm_config
    )
    
    # Extract and return the release notes
    return response.choices[0].message.content.strip()

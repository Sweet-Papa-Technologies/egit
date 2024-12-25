"""
LLM integration for eGit using LiteLLM
"""
from typing import Optional, List, Dict, Any
from litellm import completion
from .config import load_config, get_config
import os

SUMMARY_PROMPT = """
You are a helpful assistant that summarizes Git commit messages. Please summarize all of the changes this person has made to their code based off the commit messages.
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

# async def summarize_commits(commit_messages: str) -> str:
#     """Summarize commit messages using LLM"""
#     prompt = SUMMARY_PROMPT.format(context=commit_messages)
#     return await get_llm_response(prompt)

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
    
    # Create a more specific system prompt
    system_prompt = """
    You are a Git commit message generator that creates clear, concise, and informative summaries of code changes.
    You will be given a list of changed files and their git diffs. Your task is to write a commit message that explains what changed.

    Follow these rules for the commit message:
    1. Start with a verb in the present tense (e.g., "Add", "Fix", "Update", "Refactor")
    2. Do not use words like "seems" or "appears", speak with confidence
    3. Focus on the actual code changes shown in the diff, not just the file names
    4. Mention specific components or features that were modified
    5. Include any breaking changes or important notes
    6. DO NOT use the word "summary" or phrases like "this commit"
    7. DO NOT Write multiple paragraphs or use line breaks
    8. DO NOT Use generic phrases like "various changes" or "multiple updates"
    9. DO NOT Simply list the files that changed
    10. DO NOT GIVE FEEDBACK ON THE CODE, JUST SUMMARIZE THE CHANGES

    ONLY RESPOND WITH THE COMMIT MESSAGE

    """

    # Create a more structured user prompt
    prompt = f"""Here are the Git changes to summarize:

    Changed Files:
    {changes_text}

    Git Diff:
    {diff_text}

    Write a Git commit message that describes these changes.
    Focus on the actual code changes shown in the diff, not just which files were modified.
    The message should be a single line.

    ONLY RESPOND WITH THE COMMIT MESSAGE
    """

    # print("Using the Following Prompt:")
    # print(prompt)

    # print("Using the Following System Prompt:")
    # print(system_prompt)

    # Get response from LLM
    try:
        model = config.get("llm_model", "ollama/llama3.2:3b")
        if config.get("llm_provider") == "ollama":
            # Strip 'openai/' prefix for Ollama models
            model = model.replace("openai/", "ollama/")
        print(f"Using model: {model}")

        MESSAGES = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # print("Using the Following Messages:")
        print(MESSAGES)

        response = completion(
            model=model,
            messages=MESSAGES,
            temperature=float(config.get("llm_temperature", 0.7)),
            max_tokens=int(config.get("llm_max_tokens", 4096)),
            api_key=config.get("llm_api_key", "sk-123"),
            api_base=config.get("llm_api_base", "http://localhost:11434")
        )
        
        # Clean up the response
        summary = response.choices[0].message.content.strip()
                
        return summary
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

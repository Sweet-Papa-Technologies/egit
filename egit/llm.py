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

def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration"""
    config = get_config()
    setup_llm_env()
    model = config.get("llm_model", "ollama/llama3.2:3b")
    if config.get("llm_provider") == "ollama":
        model = model.replace("openai/", "ollama/")

    LLM_CONFIG = {
        "model": model,
        "api_base": config.get("llm_api_base", "http://localhost:11434"),
        "api_key": config.get("llm_api_key", "sk-123"),
        "max_tokens": int(config.get("llm_max_tokens", "500")),
        "temperature": float(config.get("llm_temperature", "0.7")),
    }

    provider = config.get("llm_provider", "ollama").lower() 
    
    if provider == "gemini" or provider == "vertex_ai":
        LLM_CONFIG["api_base"] = None # Let LiteLLM handle this

    print(f"Using LLM model: {LLM_CONFIG['model']}")
    
    return LLM_CONFIG

async def get_llm_response(prompt: str, max_tokens: Optional[int] = None) -> str:
    """Get response from LLM"""
    config = get_config()
    setup_llm_env()
    
    try:
        llm_config = get_llm_config()
        response = await completion(
            messages=[{"role": "user", "content": prompt}],
            **llm_config
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error getting LLM response: {str(e)}")

def summarize_changes(changes: List[str], diffs: List[str]) -> str:
    """Generate a natural language summary of the changes"""
    config = get_config()
    
    # Setup environment variables
    setup_llm_env()
    
    # Prepare the prompt with both file changes and diffs
    changes_text = "\n".join(changes)
    diff_text = "\n".join(diffs)
    
    # Create a more specific system prompt
    system_prompt = """You are a Git commit message generator. You will ONLY output a single line commit message.
    Your response must:
    1. Start with a verb in present tense
    2. Be under 72 characters
    3. Describe the main code change
    4. NOT include phrases like "this commit" or "summary"
    5. NOT explain or justify the changes
    6. NOT give suggestions or improvements
    """

    # Create a more structured user prompt
    prompt = f"""Git changes to summarize:

    Changes: {changes_text}

    Diff: {diff_text}

    INSTRUCTIONS:
    1. Write ONE LINE starting with a present-tense verb
    2. Focus on what changed in the code
    3. Keep it under 72 characters
    4. Do not explain or justify anything
    5. Do not make suggestions

    BAD: "This commit improves the code by updating the git handling system which could be made better by..."
    GOOD: "Update git diff handling to include uncommitted changes"

    YOUR RESPONSE MUST BE EXACTLY ONE LINE WITH NO EXPLANATION OR EXTRA TEXT.
    RESPOND WITH ONLY THE COMMIT MESSAGE:
    """

    # print("Using the Following Prompt:")
    # print(prompt)

    # print("Using the Following System Prompt:")
    # print(system_prompt)

    # Get response from LLM
    try:
        MESSAGES = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # print("Using the Following Messages:")
        # print(MESSAGES)

        llm_config = get_llm_config()
        response = completion(
            messages=MESSAGES,
            **llm_config
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

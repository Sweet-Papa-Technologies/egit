"""
LLM integration for eGit using LiteLLM
"""
from typing import Optional
from litellm import completion
from .config import load_config

SUMMARY_PROMPT = """
You are a helpful assistant that summarizes GitLab commit messages. Please summarize all of the changes this person has made to their code based off the commit messages.
{context}
"""

RELEASE_NOTES_PROMPT = """
You are a helpful assistant that generates release notes from Git commit messages. Please generate clear and organized release notes in markdown format based on the following commit messages:
{context}
"""

async def get_llm_response(prompt: str, max_tokens: Optional[int] = None) -> str:
    """Get response from LLM"""
    config = load_config()
    
    try:
        response = await completion(
            model=config.llm_model,
            messages=[{"role": "user", "content": prompt}],
            api_base=config.llm_api_base,
            api_key=config.llm_api_key,
            max_tokens=max_tokens or config.llm_max_tokens,
            temperature=config.llm_temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error getting LLM response: {str(e)}")

async def summarize_commits(commit_messages: str) -> str:
    """Summarize commit messages using LLM"""
    prompt = SUMMARY_PROMPT.format(context=commit_messages)
    return await get_llm_response(prompt)

async def generate_release_notes(commit_messages: str) -> str:
    """Generate release notes from commit messages using LLM"""
    prompt = RELEASE_NOTES_PROMPT.format(context=commit_messages)
    return await get_llm_response(prompt)

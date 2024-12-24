"""LLM integration for eGit."""

from typing import Optional

from litellm import completion
from pydantic import BaseModel

from egit.config import settings


class LLMResponse(BaseModel):
    """Response from LLM."""
    text: str
    tokens_used: int


async def get_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> LLMResponse:
    """Get completion from LLM."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = await completion(
        model=settings.llm.model,
        messages=messages,
        api_base=settings.llm.api_base,
        max_tokens=max_tokens or settings.llm.max_tokens,
        temperature=settings.llm.temperature,
    )

    return LLMResponse(
        text=response.choices[0].message.content,
        tokens_used=response.usage.total_tokens,
    )


async def summarize_changes(diff_text: str) -> str:
    """Summarize Git changes using LLM."""
    system_prompt = """You are a helpful AI assistant that summarizes Git changes.
    Your summaries should be concise, clear, and focus on the important changes.
    Use bullet points for multiple changes."""

    prompt = f"""Please summarize the following Git changes:

{diff_text}

Focus on what was changed and why it might have been changed.
Keep the summary concise but informative."""

    response = await get_completion(prompt, system_prompt)
    return response.text

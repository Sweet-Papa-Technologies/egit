"""
LLM integration for eGit using LiteLLM
"""
from typing import Optional, List, Dict, Any
from litellm import completion
from .config import load_config, get_config
import os
import re
import time

# Cap the diff we hand the model. Free-tier Gemini allows 250k input tokens per
# minute; a first commit of a whole repo (lockfiles included) blows past that.
MAX_DIFF_CHARS = 200_000


def _truncate_diff(diff_text: str, max_chars: int = MAX_DIFF_CHARS) -> str:
    """Trim an oversized diff so the request stays inside the provider's quota"""
    if len(diff_text) <= max_chars:
        return diff_text
    omitted = len(diff_text) - max_chars
    return (
        diff_text[:max_chars]
        + f"\n\n[... diff truncated, {omitted} more characters omitted ...]"
    )


def _is_rate_limit(err: Exception) -> bool:
    text = str(err)
    return (
        "RateLimit" in type(err).__name__
        or "429" in text
        or "RESOURCE_EXHAUSTED" in text
    )


def _completion_with_retry(messages: List[Dict[str, str]], llm_config: Dict[str, Any],
                           attempts: int = 4):
    """Call the model, backing off when the provider reports a rate limit"""
    delay = 2.0
    for attempt in range(attempts):
        try:
            return completion(messages=messages, **llm_config)
        except Exception as e:
            if not _is_rate_limit(e) or attempt == attempts - 1:
                raise
            match = re.search(r'retryDelay"?:\s*"?(\d+(?:\.\d+)?)s', str(e))
            wait = float(match.group(1)) + 1 if match else delay
            print(f"Rate limited by provider, retrying in {wait:.0f}s "
                  f"(attempt {attempt + 2}/{attempts})")
            time.sleep(min(wait, 60))
            delay = min(delay * 2, 60)

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
        os.environ["OPENAI_API_BASE"] = config.get("llm_api_base", "http://localhost:11434")
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
    diff_text = _truncate_diff("\n".join(diffs))
    
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
        response = _completion_with_retry(MESSAGES, llm_config)

        # Clean up the response
        summary = response.choices[0].message.content.strip()

        if not summary:
            raise RuntimeError("Model returned an empty commit message")

        return summary
    except Exception as e:
        # Never hand the caller an error string: it would be committed verbatim.
        raise RuntimeError(f"Failed to generate summary: {e}") from e

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

# ==== Comparison-specific analysis functions ====

def analyze_file_changes(diff: str, filepath: str, model: Optional[str] = None) -> str:
    """
    Analyze a file's diff and generate a technical summary.

    Prompt template should include:
    - File path and change type (best-effort inference from diff headers)
    - Full diff content
    - Request for: purpose, impact, technical details, breaking changes
    """
    setup_llm_env()
    llm_config = get_llm_config()
    if model:
        llm_config["model"] = model

    # Best-effort inference of change type from diff header
    change_type = "Modified"
    if diff.startswith("diff --git"):
        if "\nnew file mode" in diff:
            change_type = "Added"
        elif "\ndeleted file mode" in diff:
            change_type = "Deleted"
        elif "\nrename from " in diff or "\nrename to " in diff:
            change_type = "Renamed"

    prompt = f"""You are an expert software engineer generating technical change documentation for a single file.

FILE: {filepath}
CHANGE TYPE: {change_type}

DIFF (unified):
{diff}

Requirements:
- Summarize what changed at a high level and why (inferred purpose)
- Assess impact: Low/Medium/High/Critical; call out breaking changes if present
- List technical details: new/modified functions, classes, APIs, config, data models
- Note dependencies affected or external integrations touched
- Provide 3-6 bullet points as KEY CHANGES, followed by a brief paragraph summary
- Keep language precise and factual

Output:
KEY CHANGES:
- <bullet 1>
- <bullet 2>
- <bullet 3>

SUMMARY:
<1-2 short paragraphs>
"""
    try:
        response = completion(
            messages=[
                {
                    "role": "system",
                    "content": "You write precise technical summaries of code diffs for release documentation."
                },
                {"role": "user", "content": prompt},
            ],
            **llm_config,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing {filepath}: {str(e)}"

def analyze_chunk_changes(chunk: str, chunk_index: int, total_chunks: int, filepath: str) -> str:
    """
    Analyze a chunk of a large file's diff.

    Used when file is too large for single analysis.
    """
    setup_llm_env()
    llm_config = get_llm_config()

    prompt = f"""You are analyzing chunk {chunk_index}/{total_chunks} of the diff for {filepath}.

CHUNK DIFF:
{chunk}

Summarize key changes in this chunk in 2-4 bullets and a brief 2-3 sentence note.
Focus on functional impact, technical details, and potential risks.
"""
    try:
        response = completion(
            messages=[
                {
                    "role": "system",
                    "content": "You write concise technical summaries of code diffs."
                },
                {"role": "user", "content": prompt},
            ],
            **llm_config,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing chunk {chunk_index} for {filepath}: {str(e)}"

def merge_chunk_summaries(summaries: List[str], filepath: str) -> str:
    """
    Merge multiple chunk summaries into a cohesive file summary.
    """
    setup_llm_env()
    llm_config = get_llm_config()

    joined = "\n\n".join(f"Chunk {i+1}:\n{s}" for i, s in enumerate(summaries))
    prompt = f"""You are merging chunk-level analyses into a single coherent summary for {filepath}.

CHUNK SUMMARIES:
{joined}

Produce:
- KEY CHANGES: 3-6 consolidated bullets (no duplicates)
- SUMMARY: one concise paragraph covering purpose, impact, technical details, breaking changes if any
"""
    try:
        response = completion(
            messages=[
                {
                    "role": "system",
                    "content": "You consolidate technical notes into clear release documentation."
                },
                {"role": "user", "content": prompt},
            ],
            **llm_config,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error merging summaries for {filepath}: {str(e)}"

def generate_comparison_summary(
    file_summaries: List[str],
    stats: Dict[str, int],
    from_ref: str,
    to_ref: str
) -> str:
    """
    Generate high-level project comparison summary from all file analyses.

    Prompt should synthesize across all files to identify:
    - Major themes (refactoring, new features, bug fixes)
    - Architectural changes
    - Breaking changes
    - Risk areas
    """
    setup_llm_env()
    llm_config = get_llm_config()

    bullets = []
    for s in file_summaries:
        for line in s.splitlines():
            t = line.strip()
            if t.startswith("- "):
                bullets.append(t[2:])
    bullets_text = "\n".join(f"- {b}" for b in bullets[:40])  # cap for prompt size

    prompt = f"""You are writing the executive summary for a technical change document.

REF RANGE: {from_ref} -> {to_ref}
STATS: files_changed={stats.get('files_changed', 0)}, insertions={stats.get('insertions', 0)}, deletions={stats.get('deletions', 0)}

KEY FILE-LEVEL BULLETS (subset):
{bullets_text}

Synthesize a high-level summary covering:
- Overall scope and themes (features, fixes, refactors)
- Architectural or dependency changes
- Any breaking changes and risk areas
- Impact assessment

Output 1-2 short paragraphs, precise and factual, suitable for executives and engineers.
"""
    try:
        response = completion(
            messages=[
                {
                    "role": "system",
                    "content": "You write clear executive summaries of software changes."
                },
                {"role": "user", "content": prompt},
            ],
            **llm_config,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating project summary: {str(e)}"

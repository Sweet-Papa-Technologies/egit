"""
Comparison and technical documentation generation module.
Analyzes differences between Git references and generates AI-powered summaries.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
from dataclasses import dataclass
from datetime import datetime
import hashlib

from . import git
from . import llm


@dataclass
class FileChange:
    """Represents a single file change with analysis."""
    status: str  # A, M, D, R
    path: str
    old_path: Optional[str]
    is_binary: bool
    is_subproject: bool
    diff: Optional[str]
    lines_added: int
    lines_removed: int
    ai_summary: Optional[str]


@dataclass
class ComparisonResult:
    """Complete comparison results with metadata."""
    from_ref: str
    to_ref: str
    repo_name: str
    repo_url: Optional[str]
    timestamp: datetime
    total_files_changed: int
    total_insertions: int
    total_deletions: int
    file_changes: List[FileChange]
    project_summary: Optional[str]
    key_changes: List[str]


class ComparisonEngine:
    """Main engine for comparing Git references and generating documentation."""

    def __init__(self, model_name: str, max_context_tokens: int):
        """
        Initialize comparison engine.

        Args:
            model_name: LLM model identifier (e.g., 'gemini/gemini-1.5-pro')
            max_context_tokens: Maximum context window size for the model
        """
        self.model_name = model_name
        self.max_context_tokens = max_context_tokens or estimate_model_capacity(model_name)
        self._cache: Dict[str, str] = {}  # simple in-memory cache keyed by file+diff hash

    def _get_repo_info(self) -> Tuple[str, Optional[str]]:
        """Detect repo name and remote URL."""
        try:
            repo_root = git.get_repo_root()
            repo_name = Path(repo_root).name
        except Exception:
            repo_name = "unknown-repo"
        repo_url = None
        try:
            repo_url = git.run_git_command(["config", "--get", "remote.origin.url"])
            if repo_url == "":
                repo_url = None
        except Exception:
            repo_url = None
        return repo_name, repo_url

    def compare(
        self,
        from_ref: str,
        to_ref: str,
        output_format: str = "markdown",
    ) -> ComparisonResult:
        """
        Compare two Git references and generate comprehensive documentation.

        Workflow:
        1. Normalize ref order (oldest → newest)
        2. Get all changed files with metadata
        3. Detect and filter subprojects
        4. Process files (binary vs text, chunking if needed)
        5. Generate AI summaries per file
        6. Generate project-level AI summary
        7. Format output according to template

        Args:
            from_ref: Starting reference
            to_ref: Ending reference
            output_format: 'markdown', 'json', or 'text'

        Returns:
            ComparisonResult object with all analysis
        """
        older_ref, newer_ref = git.normalize_ref_order(from_ref, to_ref)

        # Gather repo info
        repo_name, repo_url = self._get_repo_info()

        # Changed files and stats
        changed_files = git.get_changed_files_between(older_ref, newer_ref)
        stats = git.get_diff_stats(older_ref, newer_ref)
        subprojects = git.detect_subprojects(newer_ref)

        processable_files_dicts, skippable_files_dicts = self._classify_files(changed_files)

        # Map stats by path for lines added/removed
        per_file_stats: Dict[str, Dict[str, Any]] = {}
        for d in stats.get("details", []):
            per_file_stats[d["path"]] = d

        # Process skippable ones first to include them in output (no AI)
        file_changes: List[FileChange] = []
        for f in skippable_files_dicts:
            path = f["path"]
            status = f["status"]
            is_bin = git.is_binary_file(path, newer_ref)
            is_subproj = any(path.startswith(sp["path"] + "/") or path == sp["path"] for sp in subprojects)
            s = per_file_stats.get(path, {"lines_added": 0, "lines_removed": 0})
            file_changes.append(
                FileChange(
                    status=status,
                    path=path,
                    old_path=f.get("old_path"),
                    is_binary=is_bin,
                    is_subproject=is_subproj,
                    diff=None,
                    lines_added=int(s.get("lines_added", 0)),
                    lines_removed=int(s.get("lines_removed", 0)),
                    ai_summary=None,
                )
            )

        # Process text files (AI summaries)
        for f in processable_files_dicts:
            fc = self._process_file_diff(f, older_ref, newer_ref)
            # fill stats if available
            s = per_file_stats.get(fc.path)
            if s:
                fc.lines_added = int(s.get("lines_added", 0))
                fc.lines_removed = int(s.get("lines_removed", 0))
            file_changes.append(fc)

        # Generate project summary
        file_summaries = [fc.ai_summary for fc in file_changes if fc.ai_summary]
        simple_stats = {
            "files_changed": stats.get("files_changed", len(changed_files)),
            "insertions": stats.get("insertions", 0),
            "deletions": stats.get("deletions", 0),
        }
        project_summary = None
        try:
            project_summary = llm.generate_comparison_summary(
                file_summaries=file_summaries,
                stats=simple_stats,
                from_ref=older_ref,
                to_ref=newer_ref,
            )
        except Exception:
            project_summary = "Project summary unavailable due to LLM error."

        # Key changes extracted heuristically from file summaries (bullets)
        key_changes: List[str] = []
        for s in file_summaries:
            for line in s.splitlines():
                line_strip = line.strip()
                if line_strip.startswith("- "):
                    key_changes.append(line_strip[2:])
                elif line_strip.startswith("* "):
                    key_changes.append(line_strip[2:])

        result = ComparisonResult(
            from_ref=older_ref,
            to_ref=newer_ref,
            repo_name=repo_name,
            repo_url=repo_url,
            timestamp=datetime.now(),
            total_files_changed=int(simple_stats["files_changed"]),
            total_insertions=int(simple_stats["insertions"]),
            total_deletions=int(simple_stats["deletions"]),
            file_changes=file_changes,
            project_summary=project_summary,
            key_changes=key_changes,
        )

        # The caller (CLI) will use format_output() to produce the final text/markdown/json
        return result

    def _classify_files(self, changed_files: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Classify files into processable (text) and skippable (binary/subproject).

        Returns:
            (processable_files, skippable_files)
        """
        subprojects = git.detect_subprojects("HEAD")
        subproject_paths = [sp["path"] for sp in subprojects]
        processable: List[Dict] = []
        skippable: List[Dict] = []

        # Determine which subprojects to deeply analyze vs skip
        changed_paths = [cf["path"] for cf in changed_files]
        deep_subprojects: Dict[str, bool] = {}
        for sp in subproject_paths:
            deep_subprojects[sp] = self._should_process_subproject(sp, changed_paths)

        for cf in changed_files:
            path = cf["path"]
            status = cf["status"]
            is_subproj_file = any(path.startswith(sp + "/") or path == sp for sp in subproject_paths)
            if is_subproj_file and not deep_subprojects.get(next((sp for sp in subproject_paths if path.startswith(sp)), ""), False):
                skippable.append(cf)
                continue
            # Binary detection at destination ref (newer)
            try:
                is_bin = git.is_binary_file(path, ref="HEAD")
            except Exception:
                is_bin = False
            if is_bin or status == "D":
                # Deleted files have no content to analyze; mark as skippable
                skippable.append(cf)
            else:
                processable.append(cf)
        return processable, skippable

    def _should_process_subproject(self, subproject_path: str, changed_files: List[str]) -> bool:
        """
        Determine if a subproject should be deeply analyzed.

        Rules:
        - Process if < 55 files changed within subproject
        - Skip if >= 55 files changed (just note as dependency update)
        """
        count = 0
        for p in changed_files:
            if p.startswith(subproject_path + "/") or p == subproject_path:
                count += 1
        return count < 55

    def _process_file_diff(self, file_change: Dict, from_ref: str, to_ref: str) -> FileChange:
        """
        Process a single file's diff with AI analysis.

        For large files (model-dependent):
        - Gemini (1M context): Process entire diff at once
        - Smaller models (<100K context): Chunk, summarize chunks, merge summaries
        """
        path = file_change["path"]
        status = file_change["status"]
        old_path = file_change.get("old_path")

        # Build base FileChange
        fc = FileChange(
            status=status,
            path=path,
            old_path=old_path,
            is_binary=False,
            is_subproject=False,
            diff=None,
            lines_added=0,
            lines_removed=0,
            ai_summary=None,
        )

        try:
            diff_text = git.get_file_diff_between(from_ref, to_ref, path)
        except Exception:
            diff_text = ""

        fc.diff = diff_text

        # Simple cache to avoid re-analysis for identical diffs
        cache_key = hashlib.sha256((path + "\n" + diff_text).encode("utf-8")).hexdigest()
        if cache_key in self._cache:
            fc.ai_summary = self._cache[cache_key]
            return fc

        # Decide processing strategy based on model capacity
        capacity = estimate_model_capacity(self.model_name)
        # Very rough estimate: assume ~4 chars per token buffer
        max_chars = int(capacity * 4 * 0.90)

        if len(diff_text) == 0:
            # No diff (could be rename without changes), generate minimal summary
            fc.ai_summary = f"File {path} status {status}. No content diff detected."
            self._cache[cache_key] = fc.ai_summary
            return fc

        if len(diff_text) <= max_chars or "gemini" in self.model_name.lower():
            # Process entire diff
            try:
                fc.ai_summary = llm.analyze_file_changes(diff=diff_text, filepath=path, model=self.model_name)
            except Exception:
                fc.ai_summary = f"Summary unavailable for {path} due to LLM error."
        else:
            # Chunk and summarize
            chunks = self._chunk_diff_if_needed(diff_text, max_chars)
            chunk_summaries: List[str] = []
            for idx, chunk in enumerate(chunks, start=1):
                try:
                    summary = llm.analyze_chunk_changes(chunk=chunk, chunk_index=idx, total_chunks=len(chunks), filepath=path)
                except Exception:
                    summary = f"Chunk {idx} summary unavailable due to LLM error."
                chunk_summaries.append(summary)
            try:
                fc.ai_summary = llm.merge_chunk_summaries(chunk_summaries, filepath=path)
            except Exception:
                fc.ai_summary = "\n".join(chunk_summaries)

        # Cache result
        self._cache[cache_key] = fc.ai_summary
        return fc

    def _chunk_diff_if_needed(self, diff: str, max_chunk_size: int) -> List[str]:
        """
        Split diff into processable chunks if it exceeds model context.

        Smart chunking:
        - Split on file boundaries first
        - Then on hunk boundaries
        - Preserve context lines
        """
        if len(diff) <= max_chunk_size:
            return [diff]

        # Split by file boundaries: 'diff --git'
        file_blocks: List[str] = []
        current: List[str] = []
        for line in diff.splitlines():
            if line.startswith("diff --git "):
                if current:
                    file_blocks.append("\n".join(current))
                    current = []
            current.append(line)
        if current:
            file_blocks.append("\n".join(current))

        # Now chunk each block by hunk boundaries '@@'
        chunks: List[str] = []
        for block in file_blocks:
            if len(block) <= max_chunk_size:
                chunks.append(block)
                continue
            hunk = []
            size = 0
            for line in block.splitlines():
                hunk.append(line)
                size += len(line) + 1
                if line.startswith("@@") and size >= max_chunk_size:
                    # finalize the chunk at hunk boundary
                    chunks.append("\n".join(hunk))
                    hunk = []
                    size = 0
            if hunk:
                chunks.append("\n".join(hunk))

        # If still any chunk drastically exceeds, hard split
        final_chunks: List[str] = []
        for c in chunks:
            if len(c) <= max_chunk_size:
                final_chunks.append(c)
            else:
                # Hard split by size, preserving line boundaries
                lines = c.splitlines()
                buf: List[str] = []
                cur_size = 0
                for ln in lines:
                    if cur_size + len(ln) + 1 > max_chunk_size and buf:
                        final_chunks.append("\n".join(buf))
                        buf = []
                        cur_size = 0
                    buf.append(ln)
                    cur_size += len(ln) + 1
                if buf:
                    final_chunks.append("\n".join(buf))
        # Ensure trailing newline is preserved when rejoining chunks
        if diff.endswith("\n"):
            final_chunks.append("")
        return final_chunks

    def _generate_file_summary(self, file_change: FileChange) -> str:
        """
        Generate AI summary for a single file's changes.

        Prompt should ask for:
        - What changed (high-level)
        - Why it might have changed (inferred purpose)
        - Impact/significance (breaking changes, new features, bug fixes)
        - Technical details (new functions/classes/APIs)
        """
        # Delegated to llm.analyze_file_changes in _process_file_diff
        return file_change.ai_summary or ""

    def _generate_project_summary(self, result: ComparisonResult) -> str:
        """
        Generate high-level project summary from all file changes.

        Prompt should synthesize:
        - Overall scope of changes
        - Major features/fixes/refactors
        - Breaking changes
        - New dependencies or architectural changes
        """
        return result.project_summary or ""

    def format_output(self, result: ComparisonResult, format: str) -> str:
        """
        Format ComparisonResult according to AutoTecDoc template.

        Formats:
        - 'markdown': Human-readable markdown with sections
        - 'json': Structured JSON for programmatic use
        - 'text': Plain text following template exactly
        """
        # Compute additional stats
        status_counts = {"A": 0, "M": 0, "D": 0, "R": 0}
        binary_count = 0
        subprojects_updated: Dict[str, bool] = {}
        for fc in result.file_changes:
            if fc.status in status_counts:
                status_counts[fc.status] += 1
            if fc.is_binary:
                binary_count += 1
            # Mark subproject paths for listing
            for sp in git.detect_subprojects(result.to_ref):
                if fc.path.startswith(sp["path"] + "/") or fc.path == sp["path"]:
                    subprojects_updated[sp["path"]] = True

        if format == "json":
            # Return structured JSON
            payload = {
                "project": result.repo_name,
                "vc_url": result.repo_url,
                "doc_gen_date": result.timestamp.strftime("%m/%d/%Y"),
                "current_release": result.to_ref,
                "previous_release": result.from_ref,
                "executive_summary": result.project_summary,
                "files": [
                    {
                        "file": fc.path,
                        "status": fc.status,
                        "impact": "Medium",  # Placeholder impact - could be derived from AI
                        "summary": fc.ai_summary,
                        "key_changes": [],  # Could parse bullets from ai_summary
                        "technical_details": {
                            "new_apis": [],
                            "breaking_changes": [],
                            "dependencies": [],
                        },
                        "binary": fc.is_binary,
                        "subproject": fc.is_subproject,
                        "lines_added": fc.lines_added,
                        "lines_removed": fc.lines_removed,
                        "old_path": fc.old_path,
                    }
                    for fc in result.file_changes
                ],
                "statistics": {
                    "total_files_changed": result.total_files_changed,
                    "files_added": status_counts["A"],
                    "files_modified": status_counts["M"],
                    "files_deleted": status_counts["D"],
                    "lines_added": result.total_insertions,
                    "lines_removed": result.total_deletions,
                    "binary_files_changed": binary_count,
                    "subprojects_updated": list(subprojects_updated.keys()),
                },
            }
            return json.dumps(payload, indent=2)

        # Build plain text/markdown following template exactly
        def header() -> str:
            return (
                "========================================================================================\n"
                f"PROJECT: {result.repo_name}\n"
                f"VC URL: {result.repo_url or ''}\n"
                f"DOC GEN. DATE: {result.timestamp.strftime('%m/%d/%Y')}\n"
                f"CURRENT RELEASE: {result.to_ref}\n"
                f"PREVIOUS RELEASE: {result.from_ref}\n"
                "========================================================================================"
            )

        def exec_summary() -> str:
            return (
                "EXECUTIVE SUMMARY:\n"
                f"{result.project_summary or ''}\n"
            )

        def file_level_changes() -> str:
            out_lines = []
            out_lines.append("========================================================================================")
            out_lines.append("FILE-LEVEL CHANGES:")
            out_lines.append("========================================================================================")
            out_lines.append("")
            for fc in result.file_changes:
                out_lines.append(f"FILE: {fc.path}")
                # Human readable status
                status_map = {"A": "Added", "M": "Modified", "D": "Deleted", "R": "Renamed"}
                human_status = status_map.get(fc.status, fc.status)
                out_lines.append(f"STATUS: {human_status}")
                # Impact - simple heuristic based on lines changed
                impact = "Low"
                total_lines = fc.lines_added + fc.lines_removed
                if total_lines > 500:
                    impact = "High"
                elif total_lines > 100:
                    impact = "Medium"
                out_lines.append(f"IMPACT: {impact}")
                out_lines.append("SUMMARY:")
                out_lines.append(f"{fc.ai_summary or ''}")
                out_lines.append("")
                out_lines.append("KEY CHANGES:")
                # Extract up to 3 key bullets from AI summary
                bullets = []
                for line in (fc.ai_summary or "").splitlines():
                    line_strip = line.strip()
                    if line_strip.startswith("- "):
                        bullets.append(line_strip)
                    if len(bullets) >= 3:
                        break
                if not bullets:
                    bullets = ["- No key changes identified"]
                out_lines.extend(bullets)
                out_lines.append("")
                out_lines.append("TECHNICAL DETAILS:")
                out_lines.append("- [New functions/classes/APIs]")
                out_lines.append("- [Breaking changes]")
                out_lines.append("- [Dependencies affected]")
                out_lines.append("")
                out_lines.append("---")
                out_lines.append("")
            return "\n".join(out_lines)

        def statistics() -> str:
            return (
                "========================================================================================\n"
                "STATISTICS:\n"
                "========================================================================================\n"
                f"Total Files Changed: {result.total_files_changed}\n"
                f"Files Added: {status_counts['A']}\n"
                f"Files Modified: {status_counts['M']}\n"
                f"Files Deleted: {status_counts['D']}\n"
                f"Lines Added: {result.total_insertions}\n"
                f"Lines Removed: {result.total_deletions}\n"
                f"Binary Files Changed: {binary_count}\n"
                f"Subprojects Updated: {', '.join(list(subprojects_updated.keys()))}\n"
                "\n"
                "========================================================================================\n"
            )

        body = "\n".join([header(), exec_summary(), "", file_level_changes(), "", statistics()])
        return body

def estimate_model_capacity(model_name: str) -> int:
    """
    Estimate context window size for a given model.

    Mappings:
    - gemini/*: 1,000,000 tokens
    - gpt-4: 128,000 tokens
    - claude-3.5-sonnet: 200,000 tokens
    - Default: 8,000 tokens
    """
    name = (model_name or "").lower()
    if name.startswith("gemini") or "gemini" in name:
        return 1_000_000
    if name.startswith("gpt-4") or "gpt-4" in name:
        return 128_000
    if "claude-3.5-sonnet" in name or "claude" in name:
        return 200_000
    return 8_000

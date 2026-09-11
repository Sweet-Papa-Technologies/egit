"""
Tests for compare feature and supporting utilities
"""
import pytest
from typing import List, Dict, Any
from egit.compare import ComparisonEngine, estimate_model_capacity
from egit import git, llm

def test_normalize_ref_order(mocker):
    """normalize_ref_order should return (older, newer) based on commit timestamp"""
    # Mock run_git_command to return timestamps based on ref
    def fake_run_git_command(args: List[str], cwd=None):
        # args example: ["log", "-1", "--format=%ct", ref]
        ref = args[-1]
        if ref == "old":
            return "100"
        if ref == "new":
            return "200"
        return "0"
    mocker.patch("egit.git.run_git_command", side_effect=fake_run_git_command)

    older, newer = git.normalize_ref_order("new", "old")
    assert older == "old"
    assert newer == "new"

def test_classify_files_binary_detection(mocker):
    """_classify_files should classify binary files as skippable"""
    # Engine setup
    engine = ComparisonEngine(model_name="ollama/llama3.2:3b", max_context_tokens=estimate_model_capacity("ollama/llama3.2:3b"))
    # Mock subprojects detection: none
    mocker.patch("egit.git.detect_subprojects", return_value=[])
    # Mock binary detection: mark assets/image.png as binary
    def fake_is_binary(path: str, ref=None):
        return path.endswith(".png")
    mocker.patch("egit.git.is_binary_file", side_effect=fake_is_binary)

    changed_files = [
        {"status": "M", "path": "src/app.py", "old_path": None},
        {"status": "A", "path": "assets/image.png", "old_path": None},
        {"status": "D", "path": "docs/old.md", "old_path": None},
    ]
    processable, skippable = engine._classify_files(changed_files)

    # src/app.py should be processable
    assert any(cf["path"] == "src/app.py" for cf in processable)
    # image.png is binary; docs/old.md is deleted -> both skippable
    assert any(cf["path"] == "assets/image.png" for cf in skippable)
    assert any(cf["path"] == "docs/old.md" for cf in skippable)

def test_should_process_subproject_threshold(mocker):
    """_should_process_subproject applies 55-file threshold"""
    engine = ComparisonEngine(model_name="ollama/llama3.2:3b", max_context_tokens=estimate_model_capacity("ollama/llama3.2:3b"))
    sub_path = "packages/lib"

    # 54 changes -> should process
    files_54 = [f"{sub_path}/file{i}.py" for i in range(54)]
    assert engine._should_process_subproject(sub_path, files_54) is True

    # 55 changes -> should skip deep analysis
    files_55 = [f"{sub_path}/file{i}.py" for i in range(55)]
    assert engine._should_process_subproject(sub_path, files_55) is False

def test_chunk_diff_if_needed_preserves_boundaries():
    """_chunk_diff_if_needed should split on file and hunk boundaries, preserving content"""
    engine = ComparisonEngine(model_name="ollama/llama3.2:3b", max_context_tokens=estimate_model_capacity("ollama/llama3.2:3b"))

    diff_text = (
        "diff --git a/file1 b/file1\n"
        "--- a/file1\n"
        "+++ b/file1\n"
        "@@ hunk 1 @@\n"
        "- old\n"
        "+ new\n"
        "@@ hunk 2 @@\n"
        "- old2\n"
        "+ new2\n"
        "diff --git a/file2 b/file2\n"
        "--- a/file2\n"
        "+++ b/file2\n"
        "@@ hunk 1 @@\n"
        "+ x\n"
    )
    # Small chunk size to force multiple chunks
    chunks = engine._chunk_diff_if_needed(diff_text, max_chunk_size=60)
    assert isinstance(chunks, list)
    assert len(chunks) > 1
    # All chunks must be within the size limit
    assert all(len(c) <= 60 for c in chunks)
    # Rejoining chunks should reconstruct the original diff text exactly
    assert "\n".join(chunks) == diff_text

def test_integration_compare_and_format(mocker):
    """Full integration test: engine.compare with mock LLM, verify template output"""
    # Mock repo info
    mocker.patch("egit.compare.ComparisonEngine._get_repo_info", return_value=("egit", "https://github.com/Sweet-Papa-Technologies/egit.git"))
    # Mock ref normalization
    mocker.patch("egit.git.normalize_ref_order", return_value=("v1.0.0", "v2.0.0"))
    # Mock changed files
    changed_files = [
        {"status": "M", "path": "src/app.py", "old_path": None},
        {"status": "A", "path": "assets/image.png", "old_path": None},
    ]
    mocker.patch("egit.git.get_changed_files_between", return_value=changed_files)
    # Mock stats
    stats = {
        "files_changed": 2,
        "insertions": 10,
        "deletions": 5,
        "details": [
            {"path": "src/app.py", "old_path": None, "lines_added": 8, "lines_removed": 4, "status": "M"},
            {"path": "assets/image.png", "old_path": None, "lines_added": 2, "lines_removed": 1, "status": "A"},
        ],
    }
    mocker.patch("egit.git.get_diff_stats", return_value=stats)
    # Subprojects: none
    mocker.patch("egit.git.detect_subprojects", return_value=[])
    # Binary detection
    def fake_binary(path: str, ref=None):
        return path.endswith(".png")
    mocker.patch("egit.git.is_binary_file", side_effect=fake_binary)
    # File diffs
    mocker.patch("egit.git.get_file_diff_between", return_value="diff --git a/src/app.py b/src/app.py\n@@\n- old\n+ new\n")
    # LLM analysis
    mocker.patch("egit.llm.analyze_file_changes", return_value="KEY CHANGES:\n- Updated app logic\nSUMMARY:\nApp behavior improved.")
    mocker.patch("egit.llm.generate_comparison_summary", return_value="Overall improvements and minor refactors.")

    engine = ComparisonEngine(model_name="ollama/llama3.2:3b", max_context_tokens=estimate_model_capacity("ollama/llama3.2:3b"))
    result = engine.compare("v1.0.0", "v2.0.0", output_format="text")

    # Format output as plain text template
    output = engine.format_output(result, format="text")

    # Validate template sections
    assert output.startswith("========================================================================================")
    assert f"PROJECT: {result.repo_name}" in output
    assert "VC URL:" in output
    assert "DOC GEN. DATE:" in output
    assert f"CURRENT RELEASE: {result.to_ref}" in output
    assert f"PREVIOUS RELEASE: {result.from_ref}" in output
    assert "EXECUTIVE SUMMARY:" in output
    assert "FILE-LEVEL CHANGES:" in output
    assert "STATISTICS:" in output
    assert "Total Files Changed: 2" in output
    # Verify file-level entries appear
    assert "FILE: src/app.py" in output
    assert "STATUS: Modified" in output
    # Binary count should be 1
    assert "Binary Files Changed: 1" in output

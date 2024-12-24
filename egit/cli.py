"""CLI interface for eGit."""

import asyncio
import sys
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from egit import git, llm, docker

app = typer.Typer(
    name="egit",
    help="Enhanced Git CLI with LLM support",
    add_completion=False,
)
console = Console()


def ensure_resources() -> bool:
    """Ensure all required resources are running."""
    if not docker.ensure_ollama_running():
        console.print("[red]Failed to start Ollama container[/red]")
        return False
    return True


@app.command("summarize")
def summarize(
    commit_range: Optional[str] = typer.Argument(
        None,
        help="Commit range to summarize (e.g., HEAD~3..HEAD)",
    ),
):
    """Summarize Git changes using LLM."""
    try:
        if not ensure_resources():
            sys.exit(1)
            
        repo = git.get_repo()
        diff = git.get_diff(repo, commit_range)
        if not diff:
            console.print("[yellow]No changes to summarize[/yellow]")
            return

        with console.status("[bold green]Generating summary..."):
            summary = asyncio.run(llm.summarize_changes(diff))

        console.print(Panel(
            summary,
            title="[bold]Change Summary",
            border_style="green",
        ))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command("summarize-diff")
def summarize_diff(
    commit1: str = typer.Argument(..., help="First commit"),
    commit2: str = typer.Argument(..., help="Second commit"),
):
    """Show and summarize changes between two commits."""
    try:
        if not ensure_resources():
            sys.exit(1)
            
        repo = git.get_repo()
        diff = git.get_diff(repo, f"{commit1}..{commit2}")
        if not diff:
            console.print("[yellow]No changes between commits[/yellow]")
            return

        console.print(Panel(
            diff,
            title="[bold]Git Diff",
            border_style="blue",
        ))

        with console.status("[bold green]Generating summary..."):
            summary = asyncio.run(llm.summarize_changes(diff))

        console.print(Panel(
            summary,
            title="[bold]Change Summary",
            border_style="green",
        ))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    args = sys.argv[1:]
    
    # If no arguments or help is requested, show eGit help
    if not args or args[0] in ["-h", "--help"]:
        app()
        return

    # If the command is not an eGit command, pass through to Git
    if args[0] not in app.registered_commands:
        returncode, stdout, stderr = git.pass_through(args)
        if stdout:
            console.print(stdout, end="")
        if stderr:
            console.print(stderr, end="", style="red")
        sys.exit(returncode)
    
    # Otherwise, run the eGit command
    app(args)

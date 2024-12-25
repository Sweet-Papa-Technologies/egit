"""
CLI interface for eGit
"""
import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress
from rich import print as rprint
from .config import update_config, get_config_value
from .git import get_commit_messages, get_commit_diff, get_branch_commits, execute_git_command
from .llm import summarize_commits, generate_release_notes
from .db import init_db, save_message, get_message

app = typer.Typer(help="eGit - Enhanced Git CLI with LLM capabilities")
console = Console()

@app.command()
def summarize(commit: str = "HEAD"):
    """Summarize committed changes using LLM"""
    try:
        # Check cache first
        cached = get_message(commit)
        if cached:
            rprint(f"[green]✨ Found cached summary for commit {commit}:[/green]")
            rprint(cached.generated_message)
            return

        with Progress() as progress:
            task = progress.add_task("[cyan]Getting commit summary...", total=None)
            
            # Get commit messages
            messages = get_commit_messages(commit)
            
            # Get summary from LLM
            summary = asyncio.run(summarize_commits(messages))
            
            # Save to database
            save_message(commit, messages, summary, "summarize")
            
            progress.remove_task(task)
            
        rprint(f"[green]✨ Summary for commit {commit}:[/green]")
        rprint(summary)
            
    except Exception as e:
        rprint(f"[red]Error: {str(e)}[/red]")

@app.command()
def summarize_diff(commit1: str, commit2: str):
    """Show and summarize changes between two commits"""
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Analyzing diff...", total=None)
            
            # Get diff
            diff = get_commit_diff(commit1, commit2)
            
            # Get summary from LLM
            summary = asyncio.run(summarize_commits(diff))
            
            progress.remove_task(task)
            
        rprint(f"[green]✨ Changes between {commit1} and {commit2}:[/green]")
        rprint(summary)
            
    except Exception as e:
        rprint(f"[red]Error: {str(e)}[/red]")

@app.command()
def release_notes(branch: Optional[str] = None):
    """Generate release notes for a branch"""
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating release notes...", total=None)
            
            # Get all commits on branch
            commits = get_branch_commits(branch)
            commit_messages = "\n".join([f"{sha}: {msg}" for sha, msg in commits])
            
            # Generate release notes
            notes = asyncio.run(generate_release_notes(commit_messages))
            
            progress.remove_task(task)
            
        rprint("[green]✨ Release Notes:[/green]")
        rprint(notes)
            
    except Exception as e:
        rprint(f"[red]Error: {str(e)}[/red]")

@app.command()
def config(key: Optional[str] = None, value: Optional[str] = None):
    """Get or set configuration values"""
    if key and value:
        try:
            update_config(key, value)
            rprint(f"[green]✨ Updated {key} to {value}[/green]")
        except Exception as e:
            rprint(f"[red]Error updating config: {str(e)}[/red]")
    elif key:
        try:
            value = get_config_value(key)
            if value:
                rprint(f"[green]{key}:[/green] {value}")
            else:
                rprint(f"[yellow]No value set for {key}[/yellow]")
        except Exception as e:
            rprint(f"[red]Error getting config: {str(e)}[/red]")
    else:
        rprint("[yellow]Please provide a key to get or set configuration[/yellow]")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Initialize database and handle Git passthrough"""
    if ctx.invoked_subcommand is None:
        # Initialize database
        init_db()
        
        # Pass through to Git if no eGit command is specified
        try:
            import sys
            result = execute_git_command(sys.argv[1:])
            if result:
                print(result)
        except Exception as e:
            rprint(f"[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    app()

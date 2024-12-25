"""
Command-line interface for eGit
"""
import typer
from rich.console import Console
from rich import print as rprint
from typing import Optional

from . import __version__
from . import git
from . import db
from . import llm

app = typer.Typer(
    help="eGit - Enhanced Git CLI with LLM capabilities",
    no_args_is_help=True  # Show help message when no arguments are provided
)
console = Console()

def version_callback(value: bool):
    """Callback for --version flag"""
    if value:
        rprint(f"[green]eGit version: {__version__}[/green]")
        raise typer.Exit()

@app.callback()
def common(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show eGit version and exit",
        callback=version_callback,
        is_eager=True
    )
):
    """
    eGit - Enhanced Git CLI with LLM capabilities

    Run 'egit --help' for usage information.
    """
    pass

@app.command()
def summarize(
    commit: str = typer.Argument(
        ...,
        help="Commit hash, branch name, or reference to summarize"
    )
):
    """
    Generate a natural language summary of changes in a commit or branch
    """
    try:
        # Get the commit message and changes
        message = git.get_commit_message(commit)
        changes = git.get_commit_changes(commit)
        
        # Use LLM to generate summary
        summary = llm.summarize_commits(message, changes)
        console.print(f"[bold]Commit:[/bold] {commit}")
        console.print(f"[bold]Message:[/bold] {message}")
        console.print("\n[bold]Summary:[/bold]")
        console.print(summary)
        console.print("\n[bold]Changes:[/bold]")
        for change in changes:
            console.print(f"  {change}")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def config(
    show: bool = typer.Option(
        False,
        "--show",
        help="Show current configuration"
    ),
    set_key: Optional[str] = typer.Option(
        None,
        "--set",
        help="Set configuration key (e.g., llm.model)"
    ),
    value: Optional[str] = typer.Option(
        None,
        help="Value for the configuration key"
    )
):
    """
    View or modify eGit configuration
    """
    try:
        if show:
            # Show current configuration
            config = db.get_config()
            console.print("[bold]Current Configuration:[/bold]")
            for key, value in config.items():
                console.print(f"  {key}: {value}")
        elif set_key and value:
            # Set configuration value
            db.set_config(set_key, value)
            console.print(f"[green]Set {set_key} = {value}[/green]")
        else:
            # Show help if no valid options provided
            ctx = typer.get_current_context()
            console.print(ctx.get_help())
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()

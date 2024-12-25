"""
Command-line interface for eGit
"""
import typer
from rich.console import Console
from rich import print as rprint
from typing import Optional

from . import __version__
from . import git
from . import config as config_module  # Import as config_module to avoid name conflict

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
    commit: Optional[str] = typer.Argument(
        None,
        help="Commit hash, branch name, or reference to summarize. If not provided, shows staged and current branch changes."
    ),
    staged: bool = typer.Option(
        False,
        "--staged",
        "-s",
        help="Show only staged changes"
    ),
    branch: bool = typer.Option(
        False,
        "--branch",
        "-b",
        help="Show only current branch changes"
    )
):
    """
    Generate a natural language summary of changes in a commit, branch, or staged changes
    """
    try:
        if commit:
            # Summarize specific commit
            message = git.get_commit_message(commit)
            changes = git.get_commit_changes(commit)
            
            console.print(f"[bold]Commit:[/bold] {commit}")
            console.print(f"[bold]Message:[/bold] {message}")
        else:
            changes = []
            # Get staged changes if requested or if no specific option is chosen
            if staged or (not staged and not branch):
                staged_changes = git.get_staged_changes()
                if staged_changes:
                    console.print("\n[bold cyan]Staged Changes:[/bold cyan]")
                    for change in staged_changes:
                        console.print(f"  {change}")
                    changes.extend(staged_changes)
                else:
                    console.print("[yellow]No staged changes found[/yellow]")

            # Get current branch changes if requested or if no specific option is chosen
            if branch or (not staged and not branch):
                branch_changes = git.get_branch_changes()
                if branch_changes:
                    console.print("\n[bold green]Current Branch Changes:[/bold green]")
                    for change in branch_changes:
                        console.print(f"  {change}")
                    changes.extend(branch_changes)
                else:
                    console.print("[yellow]No changes in current branch[/yellow]")

        if changes:
            # Generate and display summary
            from . import llm
            summary = llm.summarize_changes(changes)
            console.print("\n[bold]Summary:[/bold]")
            console.print(summary)
            
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
        help="Set configuration key (e.g., llm_model)"
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
            current_config = config_module.get_config()
            console.print("[bold]Current Configuration:[/bold]")
            for key, val in current_config.items():
                # Don't show API keys
                if 'api_key' in key.lower():
                    val = '****' if val else ''
                console.print(f"  {key}: {val}")
        elif set_key and value:
            # Set configuration value
            config_module.update_config(set_key, value)
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

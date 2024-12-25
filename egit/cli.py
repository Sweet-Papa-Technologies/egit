"""
Command-line interface for eGit
"""
import sys
import typer
from rich.console import Console
from rich import print as rprint
from typing import Optional, List
import subprocess

from . import __version__
from . import git
from . import config as config_module

app = typer.Typer(
    help="eGit - Enhanced Git CLI with LLM capabilities",
    add_completion=False,  # Don't add completion to avoid conflicts with git
)
console = Console()

def version_callback(value: bool):
    """Callback for --version flag"""
    if value:
        rprint(f"[green]eGit version: {__version__}[/green]")
        raise typer.Exit()

def pass_to_git(args: List[str]) -> None:
    """Pass command to git"""
    try:
        # Get git executable from config
        git_exe = config_module.get_config().get("git_executable", "git")
        # Run git command with all arguments
        result = subprocess.run([git_exe] + args, check=True)
        raise typer.Exit(result.returncode)
    except subprocess.CalledProcessError as e:
        raise typer.Exit(e.returncode)

@app.callback(invoke_without_command=True)
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
    ),
    auto_commit: bool = typer.Option(
        False,
        "--commit",
        "-c",
        help="Automatically commit changes with the generated summary"
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
            diffs = git.get_commit_diff(commit)
            
            console.print(f"[bold]Commit:[/bold] {commit}")
            console.print(f"[bold]Message:[/bold] {message}")
            console.print("\n[bold]Changes:[/bold]")
            for change in changes:
                console.print(f"  {change}")
        else:
            changes = []
            diffs = []
            staged_changes = None
            
            # Get staged changes if requested or if no specific option is chosen
            if staged or (not staged and not branch):
                staged_changes = git.get_staged_changes()
                staged_diffs = git.get_staged_diff()
                if staged_changes:
                    console.print("\n[bold cyan]Staged Changes:[/bold cyan]")
                    for change in staged_changes:
                        console.print(f"  {change}")
                    changes.extend(staged_changes)
                    diffs.extend(staged_diffs)
                else:
                    console.print("[yellow]No staged changes found[/yellow]")

            # Get current branch changes if requested or if no specific option is chosen
            if branch or (not staged and not branch):
                branch_changes = git.get_branch_changes()
                branch_diffs = git.get_branch_diff()
                if branch_changes:
                    console.print("\n[bold green]Current Branch Changes:[/bold green]")
                    for change in branch_changes:
                        console.print(f"  {change}")
                    changes.extend(branch_changes)
                    diffs.extend(branch_diffs)
                else:
                    console.print("[yellow]No changes in current branch[/yellow]")

        if changes:
            # Generate and display summary
            from . import llm
            summary = llm.summarize_changes(changes, diffs)
            console.print("\n[bold]Summary:[/bold]")
            console.print(summary)
            
            # Auto-commit if requested and there are staged changes
            if auto_commit and staged_changes:
                git.commit(summary)
                console.print("\n[green]Changes committed successfully![/green]")
            elif auto_commit:
                console.print("\n[yellow]No staged changes to commit[/yellow]")
            
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

def main():
    """Main entry point for the CLI"""
    # Print the version if requested
    console.print(f"[green]eGit version: {__version__}[/green]")
    console.print(sys.argv)

    # If no arguments, show help

    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        app(['--help'])
        return

    # Get the command (first argument after the script name)
    command = sys.argv[1]

    # If it's an eGit command, handle it with our app
    app()

if __name__ == "__main__":
    main()

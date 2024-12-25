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
def release_notes(
    version: str = typer.Argument(
        ...,
        help="Version number for the release (e.g., v1.0.0)"
    ),
    from_ref: Optional[str] = typer.Option(
        None,
        "--from",
        help="Starting reference (commit/tag) for the release notes. Defaults to last tag."
    ),
    to_ref: Optional[str] = typer.Option(
        None,
        "--to",
        help="Ending reference (commit/tag) for the release notes. Defaults to HEAD."
    ),
    create_tag: bool = typer.Option(
        False,
        "--tag",
        "-t",
        help="Create a git tag with the release notes"
    ),
    draft: bool = typer.Option(
        False,
        "--draft",
        "-d",
        help="Show draft release notes without creating a tag"
    )
):
    """
    Generate release notes for the specified version
    """
    try:
        # Validate version format
        if not version.startswith('v'):
            version = f"v{version}"
        
        # Check for uncommitted changes
        if git.has_uncommitted_changes():
            # Get staged changes
            staged_changes = git.get_staged_changes()
            if staged_changes:
                # Ask user if they want to commit first
                console.print("[yellow]You have staged changes. Would you like to commit them first?[/yellow]")
                console.print("Changes to be committed:")
                for change in staged_changes:
                    console.print(f"  {change}")
                
                if typer.confirm("Commit these changes?"):
                    
                    # Generate commit message
                    diffs = git.get_staged_diff()
                    console.print("\n[yellow]Staged Changes:[/yellow]")
                    for change in staged_changes:
                        console.print(f"  {change}")
                    console.print(f"[yellow]Commit Diff:[/yellow]")
                    for diff in diffs:
                        console.print(f"  {diff}")
                    
                    from . import llm
                    commit_msg = llm.summarize_changes(staged_changes, diffs)
                    git.commit(commit_msg)
                    console.print("[green]Changes committed successfully![/green]")
                else:
                    raise typer.Exit("Please commit or stash your changes before creating a release.")
            else:
                raise typer.Exit("Please commit or stash your changes before creating a release.")
        
        # Get commit range
        if not from_ref:
            # Get the last tag as the starting point
            try:
                from_ref = git.get_last_tag()
            except Exception:
                console.print("[yellow]No previous tags found, using root commit[/yellow]")
                from_ref = git.get_root_commit()
        
        to_ref = to_ref or "HEAD"
        
        # Get all commits in the range
        commits = git.get_commits_between(from_ref, to_ref)
        if not commits:
            console.print("[yellow]No commits found in the specified range[/yellow]")
            raise typer.Exit(1)
        
        # Generate release notes
        from . import llm
        notes = llm.generate_release_notes(commits, version)
        
        # Show the release notes
        console.print("\n[bold]Release Notes:[/bold]")
        console.print(notes)
        
        # Create tag if requested
        if create_tag and not draft:
            try:
                # Check for staged changes first
                git.create_tag(version, notes)
                console.print(f"\n[green]Created tag {version} with release notes![/green]")
                
                # Push the tag
                try:
                    git.push_tag(version)
                    console.print(f"[green]Successfully pushed tag {version} to remote![/green]")
                except Exception as e:
                    console.print(f"[yellow]Warning: Tag created but failed to push to remote: {str(e)}[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]Error creating tag:[/red] {str(e)}")
                raise typer.Exit(1)
        elif draft:
            console.print("\n[yellow]Draft mode - no tag created[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

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

            if auto_commit:
                console.print("[yellow]Auto-commit is enabled. Staged changes will be committed automatically.[/yellow]")
                staged = True

                if branch:
                    staged = False
            
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
            if auto_commit:
                try:
                    if not staged_changes:
                        raise Exception("No changes staged for commit. Stage your changes first with 'git add'")
                    git.commit(summary)
                    console.print("\n[green]Changes committed successfully![/green]")
                except Exception as e:
                    console.print(f"\n[red]Error committing changes:[/red] {str(e)}")
                    raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def config(
    ctx: typer.Context,
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
        "--value",
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
        elif set_key:
            if not value:
                # If --set is provided without --value, show the current value
                current_config = config_module.get_config()
                val = current_config.get(set_key, '')
                if 'api_key' in set_key.lower():
                    val = '****' if val else ''
                console.print(f"{set_key}: {val}")
            else:
                # Set configuration value
                config_module.update_config(set_key, value)
                console.print(f"[green]Set {set_key} = {value}[/green]")
        else:
            # Show help if no valid options provided
            console.print(ctx.get_help())
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

def main():
    """Main entry point for the CLI"""
    # Print the version if requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-v', '--version']:
        console.print(f"[green]eGit version: {__version__}[/green]")
        return

    # If no arguments or help requested, show help
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        app(['--help'])
        return

    # Run the app
    app()

if __name__ == "__main__":
    main()

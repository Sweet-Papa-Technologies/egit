"""
Installer script for eGit
"""
import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil
import venv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import site

console = Console()

def is_admin() -> bool:
    """Check if script has admin privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def check_python_version():
    """Check if Python version is 3.10 or higher"""
    if sys.version_info < (3, 10):
        console.print("[red]❌ Python 3.10 or higher is required[/red]")
        sys.exit(1)
    console.print("[green]✓ Python version check passed[/green]")

def check_git_installation():
    """Check if Git is installed"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        console.print("[green]✓ Git installation check passed[/green]")
    except subprocess.CalledProcessError:
        console.print("[red]❌ Git is not installed[/red]")
        sys.exit(1)

def get_install_dir() -> Path:
    """Get installation directory based on platform"""
    system = platform.system().lower()
    
    if system == "windows":
        base = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
        return Path(base) / "egit"
    else:
        return Path.home() / ".egit"

def setup_venv(install_dir: Path):
    """Create and setup virtual environment"""
    venv_dir = install_dir / ".venv"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Create virtual environment
        task = progress.add_task("Creating virtual environment...", total=None)
        venv.create(venv_dir, with_pip=True)
        progress.remove_task(task)
        
        # Get pip path
        if platform.system().lower() == "windows":
            pip_path = venv_dir / "Scripts" / "pip.exe"
        else:
            pip_path = venv_dir / "bin" / "pip"
        
        # Install requirements
        task = progress.add_task("Installing dependencies...", total=None)
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        progress.remove_task(task)

def add_to_path(install_dir: Path):
    """Add eGit to system PATH"""
    system = platform.system().lower()
    
    if system == "windows":
        if not is_admin():
            console.print("[yellow]⚠️ Admin privileges required to modify PATH[/yellow]")
            return
        
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            current_path = winreg.QueryValueEx(key, "PATH")[0]
            if str(install_dir) not in current_path:
                new_path = f"{current_path};{install_dir}"
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
    else:
        # Add to .bashrc or .zshrc
        shell_rc = Path.home() / (".zshrc" if os.path.exists(Path.home() / ".zshrc") else ".bashrc")
        with open(shell_rc, "a") as f:
            f.write(f'\nexport PATH="$PATH:{install_dir}"\n')

def main():
    """Main installation function"""
    console.print("[bold cyan]🚀 Installing eGit...[/bold cyan]")
    
    # Check requirements
    check_python_version()
    check_git_installation()
    
    # Get installation directory
    install_dir = get_install_dir()
    console.print(f"[cyan]📁 Installing to {install_dir}[/cyan]")
    
    # Create installation directory
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup virtual environment
    setup_venv(install_dir)
    
    # Add to PATH
    add_to_path(install_dir)
    
    console.print("[bold green]✨ eGit installation complete![/bold green]")
    console.print("\nTo get started, try:")
    console.print("  egit --help")
    console.print("  egit config --help")
    console.print("  egit summarize HEAD")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"[red]❌ Installation failed: {str(e)}[/red]")
        sys.exit(1)

"""
Installer script for eGit
"""
import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def is_admin() -> bool:
    """Check if script has admin privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def get_install_dir() -> Path:
    """Get installation directory based on platform"""
    system = platform.system().lower()
    
    if system == "windows":
        base = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
        return Path(base) / "egit"
    else:
        return Path.home() / ".egit"

def is_installed(install_dir: Path) -> bool:
    """Check if eGit is already installed"""
    return install_dir.exists() and (install_dir / ".venv").exists()

def backup_config(install_dir: Path):
    """Backup existing configuration files"""
    config_dir = install_dir / "config_backup"
    config_dir.mkdir(exist_ok=True)
    
    # Files to backup
    backup_files = [
        install_dir / "egit.json",
        install_dir / ".env",
        install_dir / "egit.db"
    ]
    
    for file in backup_files:
        if file.exists():
            shutil.copy2(file, config_dir / file.name)
            console.print(f"[cyan]📦 Backed up {file.name}[/cyan]")

def restore_config(install_dir: Path):
    """Restore configuration files from backup"""
    config_dir = install_dir / "config_backup"
    if not config_dir.exists():
        return
    
    # Files to restore
    restore_files = [
        ("egit.json", install_dir / "egit.json"),
        (".env", install_dir / ".env"),
        ("egit.db", install_dir / "egit.db")
    ]
    
    for backup_name, target in restore_files:
        backup_file = config_dir / backup_name
        if backup_file.exists():
            shutil.copy2(backup_file, target)
            console.print(f"[cyan]📦 Restored {backup_name}[/cyan]")
    
    # Clean up backup directory
    shutil.rmtree(config_dir)

def copy_package_files(install_dir: Path):
    """Copy package files to installation directory"""
    # Get current script directory
    current_dir = Path(__file__).parent.absolute()
    
    # Copy package files
    package_dir = install_dir / "egit"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    shutil.copytree(current_dir / "egit", package_dir)
    
    # Copy other necessary files
    for file in ["requirements.txt", "setup.py", "README.md"]:
        src = current_dir / file
        if src.exists():
            shutil.copy2(src, install_dir / file)

def install_package(install_dir: Path):
    """Install the package in development mode"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Installing eGit package...", total=None)
        
        # First install requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(install_dir / "requirements.txt")
        ], check=True, encoding="utf-8")
        
        # Then install the package itself
        subprocess.run([
            sys.executable, "setup.py", "develop"
        ], check=True, cwd=str(install_dir), encoding="utf-8")
        
        progress.remove_task(task)

def add_to_path(install_dir: Path) -> bool:
    """Add eGit to system PATH. Returns True if PATH was modified, False otherwise."""
    system = platform.system().lower()
    
    if system == "windows":
        if not is_admin():
            console.print("[yellow]⚠️ To add eGit to PATH, run the following command as administrator:[/yellow]")
            console.print(f'[cyan]setx /M PATH "%PATH%;{install_dir}"[/cyan]')
            return False
        
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            current_path = winreg.QueryValueEx(key, "PATH")[0]
            if str(install_dir + "\\.venv\\Scripts") not in current_path:
                new_path = f"{current_path};{install_dir}"
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        return True
    else:
        # Add to .bashrc or .zshrc
        shell_rc = Path.home() / (".zshrc" if os.path.exists(Path.home() / ".zshrc") else ".bashrc")
        with open(shell_rc, "a") as f:
            f.write(f'\nexport PATH="$PATH:{install_dir + "/.venv/Scripts"}"\n')
        return True

def main():
    """Main installation function"""
    console.print("[bold cyan]🚀 Installing eGit...[/bold cyan]")
    
    # Get installation directory
    install_dir = get_install_dir()
    
    # Check if this is an update
    updating = is_installed(install_dir)
    if updating:
        console.print("[cyan]📦 Updating existing eGit installation...[/cyan]")
        # Backup existing configuration
        backup_config(install_dir)
    else:
        console.print(f"[cyan]📁 Installing to {install_dir}[/cyan]")
        install_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy package files
    copy_package_files(install_dir)
    
    # Install the package
    install_package(install_dir)
    
    if updating:
        # Restore configuration
        restore_config(install_dir)
        console.print("[bold green]✨ eGit update complete![/bold green]")
    
    try:
        # Add to PATH for new installations
        path_added = add_to_path(install_dir)
        console.print("[bold green]✨ eGit installation complete![/bold green]")
            
        # Show PATH usage instructions if not added automatically
        if not path_added and platform.system().lower() == "windows":
            console.print("\n[yellow]To use eGit from any directory, either:[/yellow]")
            console.print("1. Run the setx command shown above as administrator")
            console.print(f"2. Or manually add [cyan]{install_dir}[/cyan] to your PATH environment variable")
    except Exception as e:
        console.print(f"[yellow]Error adding eGit to PATH: {str(e)}[/yellow]")
    
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

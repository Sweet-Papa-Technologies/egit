#!/usr/bin/env python3
"""Installer script for eGit."""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
MINIMUM_PYTHON_VERSION = (3, 10)


def run_command(
    cmd: List[str],
    cwd: Optional[str] = None,
    shell: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            shell=shell,
            check=check,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running command: {' '.join(cmd)}[/red]")
        console.print(f"[red]Error: {e.stderr}[/red]")
        raise


def is_command_available(cmd: str) -> bool:
    """Check if a command is available in the system PATH."""
    try:
        subprocess.run(
            ["where" if platform.system() == "Windows" else "which", cmd],
            capture_output=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def install_chocolatey() -> None:
    """Install Chocolatey on Windows."""
    if is_command_available("choco"):
        return

    console.print("🍫 Installing Chocolatey...")
    powershell_cmd = (
        'Set-ExecutionPolicy Bypass -Scope Process -Force; '
        '[System.Net.ServicePointManager]::SecurityProtocol = '
        '[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
        'iex ((New-Object System.Net.WebClient).DownloadString('
        "'https://community.chocolatey.org/install.ps1'))"
    )
    
    run_command(
        ["powershell", "-Command", powershell_cmd],
        shell=True,
    )


def install_homebrew() -> None:
    """Install Homebrew on macOS."""
    if is_command_available("brew"):
        return

    console.print("🍺 Installing Homebrew...")
    install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    run_command(install_cmd, shell=True)


def install_windows_dependencies() -> None:
    """Install dependencies on Windows."""
    install_chocolatey()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Install WSL2
        if not is_command_available("wsl"):
            task = progress.add_task("Installing WSL2...", total=None)
            run_command(["choco", "install", "wsl2", "-y"])
            progress.update(task, completed=True)

        # Install Python
        if not is_command_available("python3.10"):
            task = progress.add_task("Installing Python 3.10...", total=None)
            run_command(["choco", "install", "python310", "-y"])
            progress.update(task, completed=True)

        # Install Docker
        if not is_command_available("docker"):
            task = progress.add_task("Installing Docker...", total=None)
            run_command(["choco", "install", "docker", "-y"])
            progress.update(task, completed=True)

        # Install Git
        if not is_command_available("git"):
            task = progress.add_task("Installing Git...", total=None)
            run_command(["choco", "install", "git", "-y"])
            progress.update(task, completed=True)


def install_macos_dependencies() -> None:
    """Install dependencies on macOS."""
    install_homebrew()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Install Python
        if not is_command_available("python3.10"):
            task = progress.add_task("Installing Python 3.10...", total=None)
            run_command(["brew", "install", "python@3.10"])
            progress.update(task, completed=True)

        # Install Docker
        if not is_command_available("docker"):
            task = progress.add_task("Installing Docker...", total=None)
            run_command(["brew", "install", "docker"])
            progress.update(task, completed=True)

        # Install Git
        if not is_command_available("git"):
            task = progress.add_task("Installing Git...", total=None)
            run_command(["brew", "install", "git"])
            progress.update(task, completed=True)


def install_linux_dependencies() -> None:
    """Install dependencies on Linux."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Update package list
        task = progress.add_task("Updating package list...", total=None)
        run_command(["sudo", "apt-get", "update"])
        progress.update(task, completed=True)

        # Install Python
        if not is_command_available("python3.10"):
            task = progress.add_task("Installing Python 3.10...", total=None)
            run_command(["sudo", "apt-get", "install", "-y", "python3.10"])
            progress.update(task, completed=True)

        # Install Docker
        if not is_command_available("docker"):
            task = progress.add_task("Installing Docker...", total=None)
            # Add Docker's official GPG key
            run_command([
                "curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg",
                "|", "sudo", "gpg", "--dearmor", "-o",
                "/usr/share/keyrings/docker-archive-keyring.gpg"
            ], shell=True)
            
            # Add Docker repository
            run_command([
                'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] '
                'https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | '
                'sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'
            ], shell=True)
            
            # Install Docker
            run_command(["sudo", "apt-get", "update"])
            run_command([
                "sudo", "apt-get", "install", "-y",
                "docker-ce", "docker-ce-cli", "containerd.io"
            ])
            
            # Add user to docker group
            run_command(["sudo", "usermod", "-aG", "docker", "$USER"])
            progress.update(task, completed=True)

        # Install Git
        if not is_command_available("git"):
            task = progress.add_task("Installing Git...", total=None)
            run_command(["sudo", "apt-get", "install", "-y", "git"])
            progress.update(task, completed=True)


def install_nvidia_toolkit() -> None:
    """Install NVIDIA Container Toolkit."""
    if platform.system() == "Windows":
        return  # NVIDIA toolkit is handled by Docker Desktop on Windows
    
    try:
        # Check if nvidia-smi is available
        run_command(["nvidia-smi"])
    except subprocess.CalledProcessError:
        return  # No NVIDIA GPU available
    
    console.print("🎮 Installing NVIDIA Container Toolkit...")
    
    # Add NVIDIA Container Toolkit repository
    run_command([
        "curl", "-fsSL", "https://nvidia.github.io/libnvidia-container/gpgkey",
        "|", "sudo", "gpg", "--dearmor", "-o",
        "/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg"
    ], shell=True)
    
    run_command([
        'curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | '
        'sed \'s#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g\' | '
        'sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list'
    ], shell=True)
    
    run_command(["sudo", "apt-get", "update"])
    run_command(["sudo", "apt-get", "install", "-y", "nvidia-container-toolkit"])
    run_command(["sudo", "nvidia-ctk", "runtime", "configure", "--runtime=docker"])
    run_command(["sudo", "systemctl", "restart", "docker"])


def check_python_version() -> None:
    """Check if Python version meets minimum requirements."""
    current_version = sys.version_info[:2]
    if current_version < MINIMUM_PYTHON_VERSION:
        console.print(
            f"[red]Error: Python {MINIMUM_PYTHON_VERSION[0]}.{MINIMUM_PYTHON_VERSION[1]} "
            f"or higher is required. Current version: {current_version[0]}.{current_version[1]}[/red]"
        )
        sys.exit(1)


def install_egit() -> None:
    """Install eGit package."""
    console.print("🚀 Installing eGit...")
    run_command([sys.executable, "-m", "pip", "install", "-e", "."])


def setup_ollama() -> None:
    """Set up Ollama container and download model."""
    try:
        from egit.docker import ensure_ollama_running
        console.print("🤖 Setting up Ollama and downloading model...")
        if not ensure_ollama_running():
            console.print("[red]Failed to set up Ollama container[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error setting up Ollama: {e}[/red]")
        sys.exit(1)


def main() -> None:
    """Main installation function."""
    console.print("[bold blue]eGit Installer[/bold blue]")
    console.print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install system dependencies based on platform
    system = platform.system()
    if system == "Windows":
        install_windows_dependencies()
    elif system == "Darwin":
        install_macos_dependencies()
    elif system == "Linux":
        install_linux_dependencies()
        install_nvidia_toolkit()
    else:
        console.print(f"[red]Unsupported platform: {system}[/red]")
        sys.exit(1)
    
    # Install eGit
    install_egit()
    
    # Set up Ollama and download model
    setup_ollama()
    
    console.print("\n[bold green]✨ Installation complete![/bold green]")
    console.print(
        "\n[yellow]Note: You may need to restart your terminal or log out "
        "and back in for all changes to take effect.[/yellow]"
    )


if __name__ == "__main__":
    main()

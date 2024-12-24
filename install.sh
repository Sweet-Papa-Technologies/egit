#!/bin/bash

# eGit Shell Installer
set -e

# ASCII Art
echo -e "\033[36m"
cat << "EOF"
 _____ _____ _ _   
|   __|   __|_| |_ 
|   __|  |  | |  _|
|_____|_____|_|_|  
                   
EOF
echo -e "\033[0m"

echo -e "\033[36meGit Installer for Unix-like Systems\033[0m"
echo -e "\033[36m=================================\033[0m"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo -e "\033[31mUnsupported operating system: $OSTYPE\033[0m"
    exit 1
fi

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Homebrew (macOS)
install_homebrew() {
    if ! command_exists brew; then
        echo -e "\033[33mInstalling Homebrew...\033[0m"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
}

# Install dependencies for macOS
install_macos_deps() {
    install_homebrew

    # Install Python if not present
    if ! command_exists python3.10; then
        echo -e "\033[33mInstalling Python 3.10...\033[0m"
        brew install python@3.10
    fi

    # Install Git if not present
    if ! command_exists git; then
        echo -e "\033[33mInstalling Git...\033[0m"
        brew install git
    fi
    
    # Upgrade pip
    echo -e "\033[33mUpgrading pip...\033[0m"
    python3.10 -m pip install --upgrade pip
}

# Install dependencies for Linux
install_linux_deps() {
    # Update package list
    echo -e "\033[33mUpdating package list...\033[0m"
    sudo apt-get update

    # Install Python if not present
    if ! command_exists python3.10; then
        echo -e "\033[33mInstalling Python 3.10...\033[0m"
        sudo apt-get install -y python3.10 python3.10-venv python3-pip
    fi

    # Install Git if not present
    if ! command_exists git; then
        echo -e "\033[33mInstalling Git...\033[0m"
        sudo apt-get install -y git
    fi
    
    # Upgrade pip
    echo -e "\033[33mUpgrading pip...\033[0m"
    python3.10 -m pip install --upgrade pip
}

# Install Python packages
install_python_packages() {
    echo -e "\033[33mInstalling required Python packages...\033[0m"
    python3.10 -m pip install rich typer docker pydantic litellm gitpython python-dotenv
}

# Install eGit
install_egit() {
    local install_dir="$HOME/egit"

    echo -e "\033[33mCloning eGit repository...\033[0m"
    git clone https://github.com/Sweet-Papa-Technologies/egit.git "$install_dir"

    echo -e "\033[33mInstalling Python packages...\033[0m"
    install_python_packages

    echo -e "\033[33mRunning eGit installer...\033[0m"
    cd "$install_dir"
    python3.10 install.py
}

# Main installation process
main() {
    if [ "$OS" = "macos" ]; then
        install_macos_deps
    elif [ "$OS" = "linux" ]; then
        install_linux_deps
    fi

    install_egit

    echo -e "\n\033[32mInstallation complete!\033[0m"
    echo -e "\033[33mYou may need to restart your terminal for changes to take effect.\033[0m"
}

# Run main installation
main

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
        echo -e "\033[33m🍺 Installing Homebrew...\033[0m"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
}

# Install dependencies for macOS
install_macos_deps() {
    install_homebrew

    # Install Python if not present
    if ! command_exists python3.10; then
        echo -e "\033[33m🐍 Installing Python 3.10...\033[0m"
        brew install python@3.10
    fi

    # Install Git if not present
    if ! command_exists git; then
        echo -e "\033[33m📦 Installing Git...\033[0m"
        brew install git
    fi

    # Install Docker if not present
    if ! command_exists docker; then
        echo -e "\033[33m🐳 Installing Docker...\033[0m"
        brew install docker
    fi
}

# Install dependencies for Linux
install_linux_deps() {
    # Update package list
    echo -e "\033[33m📦 Updating package list...\033[0m"
    sudo apt-get update

    # Install Python if not present
    if ! command_exists python3.10; then
        echo -e "\033[33m🐍 Installing Python 3.10...\033[0m"
        sudo apt-get install -y python3.10 python3.10-venv
    fi

    # Install Git if not present
    if ! command_exists git; then
        echo -e "\033[33m📦 Installing Git...\033[0m"
        sudo apt-get install -y git
    fi

    # Install Docker if not present
    if ! command_exists docker; then
        echo -e "\033[33m🐳 Installing Docker...\033[0m"
        # Add Docker's official GPG key
        sudo apt-get install -y ca-certificates curl gnupg
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg

        # Add Docker repository
        echo \
          "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
          sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        # Install Docker packages
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

        # Add user to docker group
        sudo usermod -aG docker $USER
        echo -e "\033[33mℹ️  You may need to log out and back in for docker group changes to take effect\033[0m"
    fi
}

# Install NVIDIA Container Toolkit for Linux
install_nvidia_toolkit() {
    if command_exists nvidia-smi; then
        echo -e "\033[33m🎮 Installing NVIDIA Container Toolkit...\033[0m"
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
        && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

        sudo apt-get update
        sudo apt-get install -y nvidia-container-toolkit
        sudo nvidia-ctk runtime configure --runtime=docker
        sudo systemctl restart docker
    fi
}

# Install eGit
install_egit() {
    local temp_dir=$(mktemp -d)
    local install_script="$temp_dir/install.py"

    echo -e "\033[33m📥 Downloading eGit installer...\033[0m"
    curl -fsSL https://raw.githubusercontent.com/Sweet-Papa-Technologies/egit/main/install.py -o "$install_script"

    echo -e "\033[33m🚀 Installing eGit...\033[0m"
    python3.10 "$install_script"

    # Cleanup
    rm -rf "$temp_dir"
}

# Main installation process
main() {
    if [ "$OS" = "macos" ]; then
        install_macos_deps
    elif [ "$OS" = "linux" ]; then
        install_linux_deps
        install_nvidia_toolkit
    fi

    install_egit

    echo -e "\n\033[32m✨ Installation complete!\033[0m"
    echo -e "\033[33mYou may need to restart your terminal for changes to take effect.\033[0m"
}

# Run main installation
main

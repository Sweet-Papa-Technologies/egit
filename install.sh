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
    python3.10 -m pip install rich typer docker pydantic pydantic-settings litellm gitpython python-dotenv
}

# Update repository
update_repository() {
    local repo_path="$1"
    pushd "$repo_path" >/dev/null
    echo -e "\033[33mUpdating eGit repository...\033[0m"
    
    # Stash any local changes
    git stash -u
    
    # Switch to main branch and pull
    git checkout main
    git pull origin main
    
    popd >/dev/null
}

# Install eGit
install_egit() {
    local install_dir="$HOME/egit"
    local max_retries=3
    local retry_count=0
    local success=false

    while [ "$success" = false ] && [ $retry_count -lt $max_retries ]; do
        if [ -d "$install_dir" ]; then
            if [ -d "$install_dir/.git" ]; then
                update_repository "$install_dir" || {
                    echo -e "\033[31mFailed to update repository\033[0m"
                    rm -rf "$install_dir"
                    retry_count=$((retry_count + 1))
                    [ $retry_count -lt $max_retries ] && {
                        echo -e "\033[33mRetrying... (Attempt $retry_count)\033[0m"
                        sleep 2
                        continue
                    }
                    return 1
                }
            else
                echo -e "\033[33mRemoving existing non-git directory...\033[0m"
                rm -rf "$install_dir"
                echo -e "\033[33mCloning eGit repository...\033[0m"
                git clone https://github.com/Sweet-Papa-Technologies/egit.git "$install_dir" || {
                    retry_count=$((retry_count + 1))
                    [ $retry_count -lt $max_retries ] && {
                        echo -e "\033[33mRetrying... (Attempt $retry_count)\033[0m"
                        sleep 2
                        continue
                    }
                    return 1
                }
            fi
        else
            echo -e "\033[33mCloning eGit repository...\033[0m"
            git clone https://github.com/Sweet-Papa-Technologies/egit.git "$install_dir" || {
                retry_count=$((retry_count + 1))
                [ $retry_count -lt $max_retries ] && {
                    echo -e "\033[33mRetrying... (Attempt $retry_count)\033[0m"
                    sleep 2
                    continue
                }
                return 1
            }
        fi

        # Verify repository was cloned successfully
        if [ ! -f "$install_dir/install.py" ]; then
            echo -e "\033[31mRepository clone seems incomplete. Missing install.py\033[0m"
            rm -rf "$install_dir"
            retry_count=$((retry_count + 1))
            [ $retry_count -lt $max_retries ] && {
                echo -e "\033[33mRetrying... (Attempt $retry_count)\033[0m"
                sleep 2
                continue
            }
            return 1
        fi

        echo -e "\033[33mInstalling Python packages...\033[0m"
        install_python_packages

        echo -e "\033[33mRunning eGit installer...\033[0m"
        cd "$install_dir"
        
        # Run installer with timeout
        if timeout 300 python3.10 install.py; then
            success=true
        else
            local exit_code=$?
            if [ $exit_code -eq 124 ]; then
                echo -e "\033[31mInstallation timed out after 300 seconds.\033[0m"
                echo -e "\033[31mThis might be due to Docker installation taking too long.\033[0m"
                echo -e "\033[33mPlease try running 'python3.10 install.py' manually in $install_dir\033[0m"
                return 1
            else
                retry_count=$((retry_count + 1))
                [ $retry_count -lt $max_retries ] && {
                    echo -e "\033[33mRetrying... (Attempt $retry_count)\033[0m"
                    sleep 2
                    continue
                }
                return 1
            fi
        fi
    done

    [ "$success" = false ] && {
        echo -e "\033[31mFailed to install after $max_retries attempts\033[0m"
        return 1
    }
}

# Main installation process
main() {
    if [ "$OS" = "macos" ]; then
        install_macos_deps
    elif [ "$OS" = "linux" ]; then
        install_linux_deps
    fi

    install_egit || {
        echo -e "\033[31mInstallation failed\033[0m"
        exit 1
    }

    echo -e "\n\033[32mInstallation complete!\033[0m"
    echo -e "\033[33mYou may need to restart your terminal for changes to take effect.\033[0m"
}

# Run main installation
main

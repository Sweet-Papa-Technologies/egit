# eGit Planning

## Requirements
- Will support both local and remote models (Ollama API, OpenAI Like API, Google Vertex, and Anthropic) via LiteLLM
- The app should be written in a clean and modualar way
- The app should use Typing to enforce type checking
- The app should use Pydantic to enforce data validation
- The app should use Pytest to test the code
- Functions to send inference to LLM
- Will install Ollama via a Docker container
- User can set user configuration via command line or ENV variables
- Secrets will be stored in Env variables
- Will use a strong local model with a nice context window (At Least 32k tokens)
- Will pass any non-egit commands to Git
- Supports CPU, NVIDIA GPU, and AMD GPU
- Functions to start, stop, and restart Ollama and the Docker services / container
- Pretty output, especially for the installer script (use emojis, colors, and animations)
- Will use ENV variables to configure LLM and user settings
- Will use a config file to configure app settings (stored in the user's home directory)
- Dedicated command and script for installing this application (a one-liner for Windows, Linux, and macOS). Includes robust error handling
    - Will install Git if not already installed, checks for Git version
    - Will install Python 3.10 if not already installed
    - For Windows, we will install WSL2, Nvidia Toolkit and Docker if Docker Desktop is not already installed or Docker is not installed
    - For Linux, we will install Docker and Nvidia Toolkit if not already installed
    - For macOS, we will install Docker if not installed
    - Will install Chocolatey if not already installed
    - Will install Homebrew if not already installed
    - Will add CLI commands to PATH


## Specificications
- App will be written in Python and will be a CLI app
- LiteLLM for LLM API management
- GitPython for Git API management
- Package Managers:
    - Chocolatey for Windows
      - WSL2 Installer: `choco install wsl2`
      - Python Installer: `choco install python310`
      - Docker Installer: `choco install docker`
      - Git Installer: `choco install git`
    - Homebrew for macOS
      - Git Installer: `brew install git`
      - Python Installer: `brew install python@3.10`
      - Docker Installer: `brew install docker`
    - Apt for Linux (Debian or Ubuntu)
      - Git Installer: `sudo apt-get install git`
      - Python Installer: See Script Below
      - Docker Installer: See Script Below
    
 
## Features
- `egit summarize` - Summarize commited changes using model
- `egit summarize-diff` - Show changes between two commits and summarize changes using model

## System Requirements
- 8 GB of RAM or Higher for local models
- 4 GB of RAM or Higher for online models
- macOS, Linux (Debian or Ubuntu), or Windows

## Resources

### Homebrew (macOS)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Homebrew Installs (macOS)
```bash
brew install git
brew install python@3.10
brew install docker
```
### Chocolatey (Windows)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### Chocolatey Installs (Windows)
```powershell
choco install wsl2
choco install python310
choco install docker
choco install git
```

### Container Toolkit Install (WSL2, Docker, and Nvidia Toolkit)
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Docker Commands:
```bash
# Pull Ollama Image
docker pull ollama/ollama
```

```bash
# Start Ollama CPU Only
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

```bash
# Start Ollama with GPU
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

```bash
# AMD GPU
docker run -d --device /dev/kfd --device /dev/dri -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama:rocm
```

### Linux (Python 3.10 install)
```bash
#!/bin/bash

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (with sudo)"
    exit 1
fi

# Set error handling
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo "\"${last_command}\" command failed with exit code $?."' ERR

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Starting Python 3.10 installation..."

# Update package lists
echo "Updating package lists..."
apt-get update

# Install required dependencies
echo "Installing dependencies..."
apt-get install -y \
    software-properties-common \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python-openssl

# Add deadsnakes PPA if not already added
if ! grep -q "^deb .*deadsnakes/ppa" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
    echo "Adding deadsnakes PPA..."
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update
fi

# Install Python 3.10
echo "Installing Python 3.10..."
apt-get install -y python3.10 python3.10-venv python3.10-dev

# Install pip for Python 3.10
echo "Installing pip..."
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.10 get-pip.py
rm get-pip.py

# Verify installation
echo "Verifying installation..."
if command_exists python3.10; then
    echo "Python 3.10 installed successfully!"
    python3.10 --version
    pip3.10 --version
else
    echo "Installation failed!"
    exit 1
fi

# Create symbolic links (optional)
read -p "Do you want to create symbolic links for python3 and pip3? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating symbolic links..."
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.10 1
    echo "Symbolic links created successfully!"
fi

echo "Installation complete!"
```

### Docker Install Linux:
```bash
#!/bin/bash

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (with sudo)"
    exit 1
fi

# Set error handling
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo "\"${last_command}\" command failed with exit code $?."' ERR

# Function to detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        echo "Cannot detect OS"
        exit 1
    fi
}

# Function to install Docker on Ubuntu/Debian
install_docker_debian() {
    # Remove old versions
    apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Update package index
    apt-get update
    
    # Install prerequisites
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/${OS}/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up the repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/${OS} \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package index again
    apt-get update
    
    # Install Docker Engine
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
}

# Function to install Docker on RHEL/CentOS
install_docker_rhel() {
    # Remove old versions
    yum remove -y docker docker-engine docker.io containerd runc || true
    
    # Install prerequisites
    yum install -y yum-utils
    
    # Add Docker repository
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    # Install Docker Engine
    yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start Docker
    systemctl start docker
    systemctl enable docker
}

# Main installation process
echo "Starting Docker installation..."

# Detect OS
detect_os
echo "Detected OS: $OS $VERSION"

# Install Docker based on OS
case $OS in
    "ubuntu"|"debian")
        echo "Installing Docker for Ubuntu/Debian..."
        install_docker_debian
        ;;
    "rhel"|"centos")
        echo "Installing Docker for RHEL/CentOS..."
        install_docker_rhel
        ;;
    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac

# Verify installation
if command -v docker &> /dev/null; then
    echo "Docker installed successfully!"
    docker --version
    docker compose version
else
    echo "Docker installation failed!"
    exit 1
fi

# Add current user to docker group
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker $SUDO_USER
    echo "Added user $SUDO_USER to docker group"
    echo "Please log out and back in for this to take effect"
fi

# Test Docker
echo "Testing Docker installation..."
docker run hello-world

echo "Installation complete!"
echo "You may need to log out and back in for group changes to take effect"
```
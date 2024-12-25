#!/bin/bash

# ANSI color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}[>>] Preparing to install eGit...${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[x] Python 3 is not installed. Please install Python 3.10 or higher${NC}"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$python_version < 3.10" | bc -l) )); then
    echo -e "${RED}[x] Python 3.10 or higher is required (found $python_version)${NC}"
    exit 1
fi
echo -e "${GREEN}[+] Python version check passed${NC}"

# Check Git installation
if ! command -v git &> /dev/null; then
    echo -e "${RED}[x] Git is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}[+] Git installation check passed${NC}"

# Determine installation directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    install_dir="$HOME/.egit"
else
    # Linux
    install_dir="$HOME/.egit"
fi

# Create installation directory if it doesn't exist
mkdir -p "$install_dir"

# Create and activate virtual environment
echo -e "${CYAN}[*] Creating virtual environment...${NC}"
python3 -m venv "$install_dir/.venv"

# Install required packages
echo -e "${CYAN}[*] Installing required packages...${NC}"
"$install_dir/.venv/bin/python" -m pip install --upgrade pip
"$install_dir/.venv/bin/python" -m pip install rich typer setuptools wheel

# Run the Python installer
echo -e "${CYAN}[>] Running eGit installer...${NC}"
PYTHONIOENCODING=utf-8 "$install_dir/.venv/bin/python" install.py

echo -e "${GREEN}[*] Installation preparation complete!${NC}"

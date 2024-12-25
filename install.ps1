# eGit Installation Script for Windows

# Force UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

Write-Host "[>>] Preparing to install eGit..." -ForegroundColor Cyan

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "[x] Python 3.10 or higher is required. Please install it from https://www.python.org/downloads/" -ForegroundColor Red
            exit 1
        }
    }
    Write-Host "[+] Python version check passed" -ForegroundColor Green
} catch {
    Write-Host "[x] Python is not installed or not in PATH. Please install Python 3.10 or higher from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Check Git installation
try {
    git --version | Out-Null
    Write-Host "[+] Git installation check passed" -ForegroundColor Green
} catch {
    Write-Host "[x] Git is not installed or not in PATH. Please install Git from https://git-scm.com/downloads" -ForegroundColor Red
    exit 1
}

# Determine installation directory
$installDir = "$env:ProgramData\egit"
$scriptsDir = "$installDir\.venv\Scripts"
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir | Out-Null
}

# Create and activate virtual environment
Write-Host "[*] Creating virtual environment..." -ForegroundColor Cyan
python -m venv "$installDir\.venv"

# Install required packages
Write-Host "[*] Installing required packages..." -ForegroundColor Cyan
& "$scriptsDir\python.exe" -m pip install --upgrade pip
& "$scriptsDir\python.exe" -m pip install rich typer setuptools wheel

# Run the Python installer
Write-Host "[>] Running eGit installer..." -ForegroundColor Cyan
$env:PYTHONIOENCODING = "utf-8"
& "$scriptsDir\python.exe" install.py

# Add to PATH
Write-Host "[*] Adding eGit to PATH..." -ForegroundColor Cyan
$currentPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
if ($currentPath -notlike "*$scriptsDir*") {
    try {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentPath;$scriptsDir",
            [EnvironmentVariableTarget]::Machine
        )
        Write-Host "[+] Successfully added eGit to system PATH" -ForegroundColor Green
        Write-Host "[*] Note: You may need to restart your terminal for PATH changes to take effect" -ForegroundColor Cyan
    } catch {
        Write-Host "[x] Could not add eGit to system PATH. To add it manually, run this command as administrator:" -ForegroundColor Yellow
        Write-Host "    setx /M PATH `"%PATH%;$scriptsDir`"" -ForegroundColor Cyan
    }
} else {
    Write-Host "[*] eGit is already in system PATH" -ForegroundColor Cyan
}

Write-Host "[*] Installation preparation complete!" -ForegroundColor Green

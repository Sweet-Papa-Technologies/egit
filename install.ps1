# eGit PowerShell Installer
# Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

# ASCII Art
Write-Host @"
 _____ _____ _ _   
|   __|   __|_| |_ 
|   __|  |  | |  _|
|_____|_____|_|_|  
                   
"@ -ForegroundColor Cyan

Write-Host "eGit Installer for Windows" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

function Test-Command {
    param($Command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try {
        Get-Command $Command
        return $true
    }
    catch {
        return $false
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }
}

function Install-Chocolatey {
    if (-not (Test-Command "choco")) {
        Write-Host "🍫 Installing Chocolatey..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    }
}

function Install-Dependencies {
    Install-Chocolatey

    # Install Python if not present
    if (-not (Test-Command "python")) {
        Write-Host "🐍 Installing Python 3.10..." -ForegroundColor Yellow
        choco install python310 -y
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    }

    # Install Git if not present
    if (-not (Test-Command "git")) {
        Write-Host "📦 Installing Git..." -ForegroundColor Yellow
        choco install git -y
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    }

    # Install Docker Desktop if not present
    if (-not (Test-Command "docker")) {
        Write-Host "🐳 Installing Docker Desktop..." -ForegroundColor Yellow
        choco install docker-desktop -y
        
        # Install WSL2
        Write-Host "🐧 Installing WSL2..." -ForegroundColor Yellow
        choco install wsl2 -y
    }
}

function Install-eGit {
    $tempDir = Join-Path $env:TEMP "egit-install"
    $installScript = Join-Path $tempDir "install.py"

    # Create temp directory
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

    # Download installer
    Write-Host "📥 Downloading eGit installer..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Sweet-Papa-Technologies/egit/main/install.py" -OutFile $installScript

    # Run installer
    Write-Host "🚀 Installing eGit..." -ForegroundColor Yellow
    python $installScript

    # Cleanup
    Remove-Item -Recurse -Force $tempDir
}

try {
    Install-Dependencies
    Install-eGit

    Write-Host "`n✨ Installation complete!" -ForegroundColor Green
    Write-Host "You may need to restart your terminal for changes to take effect." -ForegroundColor Yellow
}
catch {
    Write-Host "`n❌ Installation failed: $_" -ForegroundColor Red
    exit 1
}

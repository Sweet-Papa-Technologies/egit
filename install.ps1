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
}

function Install-eGit {
    $installDir = Join-Path $HOME "egit"
    
    # Clone repository
    Write-Host "📥 Cloning eGit repository..." -ForegroundColor Yellow
    git clone https://github.com/Sweet-Papa-Technologies/egit.git $installDir

    # Run installer
    Write-Host "🚀 Running eGit installer..." -ForegroundColor Yellow
    Push-Location $installDir
    python install.py
    Pop-Location
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

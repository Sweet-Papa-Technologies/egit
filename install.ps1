# eGit PowerShell Installer
# Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

Write-Host @"
 _____ _____ _ _   
|   __|   __|_| |_ 
|   __|  |  | |  _|
|_____|_____|_|_|  
                   
"@ -ForegroundColor Cyan

Write-Host "eGit Installer for Windows" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

function Test-Command($Command) {
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try {
        Get-Command $Command
        return $true
    }
    catch {
        return $False
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }
}

function Test-DockerAvailable {
    try {
        # Check if docker command exists
        if (-not (Test-Command "docker")) {
            return $False
        }

        # Try to get docker version
        $result = docker version
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $False
    }
}

function Install-Chocolatey {
    if (-not (Test-Command "choco")) {
        Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    }
}

function Install-Dependencies {
    Install-Chocolatey

    Write-Host "Installing Python 3.10..." -ForegroundColor Yellow
    choco install python310 -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    
    # Upgrade pip
    Write-Host "Upgrading pip..." -ForegroundColor Yellow
    python -m pip install --upgrade pip

    Write-Host "Installing Git..." -ForegroundColor Yellow
    choco install git -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")

    Write-Host "Installing Docker..." -ForegroundColor Yellow
    choco install docker-desktop -fdvy
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
}

function Start-DockerService {
    Write-Host "Ensuring Docker is available..." -ForegroundColor Yellow
    
    if (-not (Test-DockerAvailable)) {
        throw "Docker is not available. Please ensure Docker is installed correctly and the service is running."
    }

    # Try to start the service if it exists
    $dockerService = Get-Service -Name "docker" -ErrorAction SilentlyContinue
    if ($null -ne $dockerService -and $dockerService.Status -ne "Running") {
        Write-Host "Starting Docker service..." -ForegroundColor Yellow
        Start-Service -Name "docker"
        $retries = 30
        
        while ($retries -gt 0) {
            $dockerService.Refresh()
            if ($dockerService.Status -eq "Running") {
                break
            }
            Start-Sleep -Seconds 2
            $retries--
            Write-Host "Waiting for Docker service to start... ($retries attempts remaining)" -ForegroundColor Yellow
        }
    }
    
    # Verify Docker is responsive
    Write-Host "Verifying Docker is responsive..." -ForegroundColor Yellow
    $retries = 15
    while ($retries -gt 0) {
        try {
            $null = docker info
            Write-Host "Docker is ready!" -ForegroundColor Green
            return
        }
        catch {
            Start-Sleep -Seconds 2
            $retries--
            if ($retries -gt 0) {
                Write-Host "Waiting for Docker to be responsive... ($retries attempts remaining)" -ForegroundColor Yellow
            }
        }
    }
    throw "Docker is not responding. Please verify Docker installation and try again."
}

function Install-PythonPackages {
    Write-Host "Installing required Python packages..." -ForegroundColor Yellow
    python -m pip install rich typer docker pydantic pydantic-settings litellm gitpython python-dotenv
}

function Update-Repository {
    param(
        [string]$RepoPath
    )
    
    Push-Location $RepoPath
    Write-Host "Updating eGit repository..." -ForegroundColor Yellow
    
    # Stash any local changes
    git stash -u
    
    # Switch to main branch and pull
    git checkout main
    git pull origin main
    
    Pop-Location
}

function Install-eGit {
    $installDir = Join-Path $HOME "egit"
    $maxRetries = 3
    $retryCount = 0
    $success = $false

    while (-not $success -and $retryCount -lt $maxRetries) {
        try {
            if (Test-Path $installDir) {
                if (Test-Path (Join-Path $installDir ".git")) {
                    Update-Repository -RepoPath $installDir
                } else {
                    Write-Host "Removing existing non-git directory..." -ForegroundColor Yellow
                    Remove-Item -Recurse -Force $installDir
                    Write-Host "Cloning eGit repository..." -ForegroundColor Yellow
                    git clone https://github.com/Sweet-Papa-Technologies/egit.git $installDir
                }
            } else {
                Write-Host "Cloning eGit repository..." -ForegroundColor Yellow
                git clone https://github.com/Sweet-Papa-Technologies/egit.git $installDir
            }

            # Verify repository was cloned successfully
            if (-not (Test-Path (Join-Path $installDir "install.py"))) {
                throw "Repository clone seems incomplete. Missing install.py"
            }

            Write-Host "Installing Python packages..." -ForegroundColor Yellow
            Install-PythonPackages

            Write-Host "Running eGit installer..." -ForegroundColor Yellow
            Push-Location $installDir

            # Set environment variables for Python process
            $env:DOCKER_HOST = "npipe:////./pipe/docker_engine"
            $env:PATH = [System.Environment]::GetEnvironmentVariable("Path", "Machine")

            # Run Python directly with environment variables
            $pythonProcess = Start-Process -FilePath "python" -ArgumentList "install.py" -NoNewWindow -Wait -PassThru
            if ($pythonProcess.ExitCode -ne 0) {
                throw "Python installer failed with exit code $($pythonProcess.ExitCode)"
            }
            $success = $true
            Pop-Location
        }
        catch {
            $retryCount++
            if ($retryCount -lt $maxRetries) {
                Write-Host "Attempt $retryCount failed. Retrying..." -ForegroundColor Yellow
                Start-Sleep -Seconds 2
                # Clean up if needed
                if (Test-Path $installDir) {
                    Remove-Item -Recurse -Force $installDir -ErrorAction SilentlyContinue
                }
            } else {
                Write-Host "Failed to install after $maxRetries attempts: $_" -ForegroundColor Red
                exit 1
            }
        }
    }
}

try {
    Install-Dependencies
    Start-DockerService
    Install-eGit
    Write-Host "`nInstallation complete!" -ForegroundColor Green
    Write-Host "You may need to restart your terminal for changes to take effect." -ForegroundColor Yellow
}
catch {
    Write-Host "`nInstallation failed: $_" -ForegroundColor Red
    exit 1
}

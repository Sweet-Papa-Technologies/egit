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
        return $false
    }
    finally {
        $ErrorActionPreference = $oldPreference
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

    if (-not (Test-Command "python")) {
        Write-Host "Installing Python 3.10..." -ForegroundColor Yellow
        choco install python310 -y
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
        
        # Upgrade pip
        Write-Host "Upgrading pip..." -ForegroundColor Yellow
        python -m pip install --upgrade pip
    }

    if (-not (Test-Command "git")) {
        Write-Host "Installing Git..." -ForegroundColor Yellow
        choco install git -y
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    }

    if (-not (Test-Command "docker")) {
        Write-Host "Installing Docker..." -ForegroundColor Yellow
        choco install docker -y
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    }
}

function Start-DockerService {
    Write-Host "Ensuring Docker service is running..." -ForegroundColor Yellow
    
    # Check if Docker service exists
    $dockerService = Get-Service -Name "docker" -ErrorAction SilentlyContinue
    
    if ($null -eq $dockerService) {
        throw "Docker service not found. Please ensure Docker is installed correctly."
    }
    
    # Start Docker service if it's not running
    if ($dockerService.Status -ne "Running") {
        Start-Service -Name "docker"
        $retries = 30
        $dockerRunning = $false
        
        Write-Host "Starting Docker service..." -ForegroundColor Yellow
        while ($retries -gt 0 -and -not $dockerRunning) {
            $dockerService.Refresh()
            if ($dockerService.Status -eq "Running") {
                $dockerRunning = $true
                break
            }
            Start-Sleep -Seconds 2
            $retries--
            Write-Host "Waiting for Docker service to start... ($retries attempts remaining)" -ForegroundColor Yellow
        }
        
        if (-not $dockerRunning) {
            throw "Docker service failed to start in time"
        }
    }
    
    # Additional wait for Docker to be fully responsive
    Write-Host "Waiting for Docker to be responsive..." -ForegroundColor Yellow
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
    throw "Docker is not responding. Please try starting Docker manually."
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

            # Run Python directly and capture full output
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

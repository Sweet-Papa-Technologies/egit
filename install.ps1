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
}

function Install-PythonPackages {
    Write-Host "Installing required Python packages..." -ForegroundColor Yellow
    python -m pip install rich typer docker pydantic litellm gitpython python-dotenv
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

            # Run installer with timeout
            $job = Start-Job -ScriptBlock { 
                Set-Location $using:installDir
                python install.py 
            }
            
            $timeout = 300000 # 5 minutes timeout
            if (Wait-Job $job -Timeout $timeout) {
                Receive-Job $job
                $success = $true
            } else {
                Write-Host "Installation timed out after $timeout seconds." -ForegroundColor Red
                Write-Host "This might be due to Docker installation taking too long." -ForegroundColor Red
                Write-Host "Please try running 'python install.py' manually in $installDir" -ForegroundColor Yellow
                Stop-Job $job
                Remove-Job $job
                Pop-Location
                exit 1
            }
            
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
    Install-eGit
    Write-Host "`nInstallation complete!" -ForegroundColor Green
    Write-Host "You may need to restart your terminal for changes to take effect." -ForegroundColor Yellow
}
catch {
    Write-Host "`nInstallation failed: $_" -ForegroundColor Red
    exit 1
}

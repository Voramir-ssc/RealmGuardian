# RealmGuardian Watchdog Daemon
# Überwacht Backend & Frontend und startet sie unsichtbar neu, falls sie beendet werden.

$RepoRoot = Split-Path -Path $PSScriptRoot -Parent
$LogDir = Join-Path -Path $PSScriptRoot -ChildPath "logs"

if (!(Test-Path -Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$BackendLog = Join-Path -Path $LogDir -ChildPath "backend.log"
$FrontendLog = Join-Path -Path $LogDir -ChildPath "frontend.log"
$WatchdogLog = Join-Path -Path $LogDir -ChildPath "watchdog.log"

function Write-WatchdogLog {
    param ([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $WatchdogLog -Value "[$Timestamp] $Message"
}

Write-WatchdogLog "RealmGuardian Watchdog gestartet."

$PythonPath = "C:\Program Files\Python311\python.exe"
$VenvPython = Join-Path -Path $RepoRoot -ChildPath "backend\venv\Scripts\python.exe"
if (Test-Path -Path $VenvPython) {
    $PythonExe = $VenvPython
} else {
    $PythonExe = $PythonPath
}

$NodePath = "C:\Program Files\nodejs"
$env:Path = "$NodePath;$env:Path"

while ($true) {
    # 1. Backend-Check (Port 8000)
    $BackendRunning = $false
    try {
        $TCP = New-Object System.Net.Sockets.TcpClient
        $AsyncResult = $TCP.BeginConnect("127.0.0.1", 8000, $null, $null)
        $Wait = $AsyncResult.AsyncWaitHandle.WaitOne(1000, $false)
        if ($Wait -and $TCP.Connected) {
            $BackendRunning = $true
            $TCP.Close()
        } else {
            $TCP.Close()
        }
    } catch {
        $BackendRunning = $false
    }

    if (-not $BackendRunning) {
        Write-WatchdogLog "Backend nicht erreichbar. Starte Backend neu..."
        $BackendDir = Join-Path -Path $RepoRoot -ChildPath "backend"
        $BackendCmd = "$PythonExe -m uvicorn main:app --host 0.0.0.0 --port 8000"
        
        Start-Process -FilePath "cmd.exe" `
            -ArgumentList "/c cd /d `"$BackendDir`" && $BackendCmd >> `"$BackendLog`" 2>&1" `
            -WindowStyle Hidden
    }

    # 2. Frontend-Check (Port 5173)
    $FrontendRunning = $false
    try {
        $TCP = New-Object System.Net.Sockets.TcpClient
        $AsyncResult = $TCP.BeginConnect("127.0.0.1", 5173, $null, $null)
        $Wait = $AsyncResult.AsyncWaitHandle.WaitOne(1000, $false)
        if ($Wait -and $TCP.Connected) {
            $FrontendRunning = $true
            $TCP.Close()
        } else {
            $TCP.Close()
        }
    } catch {
        $FrontendRunning = $false
    }

    if (-not $FrontendRunning) {
        Write-WatchdogLog "Frontend nicht erreichbar. Starte Frontend neu..."
        $FrontendDir = Join-Path -Path $RepoRoot -ChildPath "frontend"
        
        Start-Process -FilePath "cmd.exe" `
            -ArgumentList "/c cd /d `"$FrontendDir`" && npm run dev >> `"$FrontendLog`" 2>&1" `
            -WindowStyle Hidden
    }

    Start-Sleep -Seconds 5
}

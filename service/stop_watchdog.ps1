# RealmGuardian Services Stopper
$watchdogs = Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*realmguardian_watchdog.ps1*' }
if ($watchdogs) {
    $watchdogs | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    Write-Host 'Watchdog beendet.'
} else {
    Write-Host 'Kein laufender Watchdog gefunden.'
}

$ports = @(8000, 5173)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            if ($conn.OwningProcess -gt 0) {
                Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
                Write-Host ("Prozess auf Port " + $port + " (PID " + $conn.OwningProcess + ") beendet.")
            }
        }
    }
}

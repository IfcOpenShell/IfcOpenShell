$processName      = "blender"
$blenderIsRunning = Get-Process -Name $processName -ErrorAction SilentlyContinue

if($blenderIsRunning -eq $null) {
    echo "Blender is not running ready for next action."
}
else {
    Write-Warning "$processName is still running - installer cannot safely proceed to next action."
    Write-Warning "Please retry after closing all running blender applications."
    exit 1
}

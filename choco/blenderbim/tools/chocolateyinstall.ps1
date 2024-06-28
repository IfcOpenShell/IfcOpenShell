$ErrorActionPreference = 'Stop'

$url64          = 'url_blenderbim_py3x_win_zip'
$checksum64     = 'sha256sum_blenderbim_py3x_win_zip'
$checksumType64 = 'sha256'

$appDataUserDir  = [System.Environment]::GetEnvironmentVariable('appdata')
$unzipTargetDir  = "$appDataUserDir\Blender Foundation\Blender\latest_blender_version_maj_min\scripts\addons"

$chocoBaseDir    = [System.Environment]::GetEnvironmentVariable('ChocolateyInstall')
$addonEnable     = "$chocoBaseDir\lib\blenderbim-nightly\tools\enable_blenderbim_addon.py"

$programFilesDir = [System.Environment]::GetEnvironmentVariable('ProgramFiles')
$blenderExePath  = "$env:ProgramFiles\Blender Foundation\Blender latest_blender_version_maj_min\blender.exe"

$processName      = "blender"
$blenderIsRunning = Get-Process -Name $processName -ErrorAction SilentlyContinue


if($blenderIsRunning -eq $null) {
    echo "attempting to install blenderbim."
    Install-ChocolateyZipPackage -PackageName $env:ChocolateyPackageName -Url64 $url64 -Checksum64 $checksum64 -checksumType $checksumType64 -UnzipLocation $unzipTargetDir
    Start-Process -FilePath  $blenderExePath -ArgumentList "-b", "-y", "--python", "$addonEnable"
}
else {
    Write-Warning "$processName is still running - blenderbim cannot be safely installed."
    Write-Warning "Please retry after closing all running blender applications."
    exit 1
}

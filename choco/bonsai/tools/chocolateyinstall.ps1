# This file was generated with the assistance of an AI coding tool.
$ErrorActionPreference = 'Stop'

# The zip is chosen for the newest Blender found: Blender 5.1 and later bundle
# Python 3.13, earlier releases Python 3.11.
$blender = Get-ChildItem "$env:ProgramFiles\Blender Foundation\Blender *\blender.exe" -ErrorAction SilentlyContinue |
  Sort-Object { [version]($_.Directory.Name -replace '^Blender ') } -Descending |
  Select-Object -First 1
if (-not $blender) {
  throw "No Blender found under '$env:ProgramFiles\Blender Foundation'. Install the 'blender' package first."
}
$blenderVersion = [version]($blender.Directory.Name -replace '^Blender ')
if ($blenderVersion -ge [version]'5.1') {
  $url = '{{URL_PY313}}'
  $checksum = '{{SHA256_PY313}}'
} else {
  $url = '{{URL_PY311}}'
  $checksum = '{{SHA256_PY311}}'
}

$zip = Join-Path $env:TEMP (($url -split '/')[-1])
Get-ChocolateyWebFile -PackageName $env:ChocolateyPackageName -FileFullPath $zip `
  -Url64bit $url -Checksum64 $checksum -ChecksumType64 'sha256'

# Blender installs and enables the extension for the current user.
& $blender.FullName --command extension install-file --repo user_default --enable $zip
if ($LASTEXITCODE -ne 0) {
  throw "Blender $blenderVersion could not install the extension (exit code $LASTEXITCODE)."
}
Remove-Item $zip

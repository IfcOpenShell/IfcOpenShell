# This file was generated with the assistance of an AI coding tool.
$ErrorActionPreference = 'Stop'

$blender = Get-ChildItem "$env:ProgramFiles\Blender Foundation\Blender *\blender.exe" -ErrorAction SilentlyContinue |
  Sort-Object { [version]($_.Directory.Name -replace '^Blender ') } -Descending |
  Select-Object -First 1
if (-not $blender) {
  Write-Warning "No Blender found under '$env:ProgramFiles\Blender Foundation'; nothing to remove."
  return
}

& $blender.FullName --command extension remove bonsai
if ($LASTEXITCODE -ne 0) {
  throw "Blender could not remove the extension (exit code $LASTEXITCODE)."
}

$ErrorActionPreference = 'Stop'
$Source = Join-Path $PSScriptRoot 'SurgMark-ESD'
$Destination = Join-Path $env:LOCALAPPDATA 'SurgMark-ESD'
if (!(Test-Path (Join-Path $Source 'index.html'))) { throw 'Extract the entire ZIP before installing.' }
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Copy-Item -Path (Join-Path $Source '*') -Destination $Destination -Recurse -Force
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'SurgMark ESD.lnk'))
$Shortcut.TargetPath = Join-Path $Destination 'index.html'
$Shortcut.WorkingDirectory = $Destination
$Shortcut.Description = 'SurgMark ESD local annotation tool'
$Shortcut.Save()
Write-Host 'Installed. Open the SurgMark ESD desktop shortcut. No Python is required for manual annotation.'
Start-Process (Join-Path $Destination 'index.html')

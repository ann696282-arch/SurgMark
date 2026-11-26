@echo off
setlocal
powershell.exe -NoProfile -File "%~dp0install-windows.ps1"
if errorlevel 1 (
 echo Installation could not finish. Open SurgMark-ESD\index.html directly, or review your local script policy with your administrator.
 pause
 exit /b 1
)
endlocal

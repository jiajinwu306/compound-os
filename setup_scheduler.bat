@echo off
REM COMPOUND.OS Daily AI News - Windows Task Scheduler setup
REM Run as administrator

setlocal
set TASK_NAME=COMPOUND.OS Daily News Fetch
set SCRIPT_DIR=%~dp0
set DAILY_BAT=%SCRIPT_DIR%run_daily.bat

echo ============================================================
echo  COMPOUND.OS Daily AI News - Task Scheduler setup
echo ============================================================
echo.
echo Task name : %TASK_NAME%
echo Entry     : %DAILY_BAT%
echo Schedule  : Daily at 10:00
echo.
echo This task runs fetch_news.py then pops a desktop notification.
echo.

if not exist "%DAILY_BAT%" (
    echo ERROR: Entry script not found: %DAILY_BAT%
    pause
    exit /b 1
)

powershell -Command "Get-Host" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell not found, cannot send notifications.
    pause
    exit /b 1
)

schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

schtasks /Create ^
  /TN "%TASK_NAME%" ^
  /TR "\"%DAILY_BAT%\"" ^
  /SC DAILY ^
  /ST 10:00 ^
  /RL HIGHEST ^
  /F

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create task. Run this batch as administrator.
    pause
    exit /b 1
)

echo.
echo OK: Daily 10:00 task created.
echo.
echo Test now : schtasks /Run /TN "%TASK_NAME%"
echo Remove   : run remove_scheduler.bat as administrator
echo.
pause
endlocal

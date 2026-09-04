@echo off
REM COMPOUND.OS Daily AI News entry point
REM Called by Windows Task Scheduler at 10:00 every day.
REM Runs fetch_news.py, then notify.ps1 on success or failure.

setlocal
set SCRIPT_DIR=%~dp0
set PYTHON_EXE=D:\python11\python.exe
set FETCH_SCRIPT=%SCRIPT_DIR%fetch_news.py
set NOTIFY_SCRIPT=%SCRIPT_DIR%notify.ps1

cd /d "%SCRIPT_DIR%"

echo [%date% %time%] Start daily fetch >> "%SCRIPT_DIR%run_daily.log"

if not exist "%PYTHON_EXE%" (
    echo [%date% %time%] ERROR: Python not found: %PYTHON_EXE% >> "%SCRIPT_DIR%run_daily.log"
    call :notify_fail
    exit /b 1
)

"%PYTHON_EXE%" "%FETCH_SCRIPT%"
if errorlevel 1 (
    echo [%date% %time%] ERROR: fetch_news.py failed >> "%SCRIPT_DIR%run_daily.log"
    call :notify_fail
    exit /b 1
)

echo [%date% %time%] OK: fetch done, sending notification >> "%SCRIPT_DIR%run_daily.log"
powershell -NoProfile -ExecutionPolicy Bypass -File "%NOTIFY_SCRIPT%" -Mode ok
exit /b 0

:notify_fail
powershell -NoProfile -ExecutionPolicy Bypass -File "%NOTIFY_SCRIPT%" -Mode fail
exit /b 1

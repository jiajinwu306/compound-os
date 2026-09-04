@echo off
REM COMPOUND.OS Daily AI News - Remove Windows Task Scheduler task
REM Run as administrator

setlocal
set TASK_NAME=COMPOUND.OS Daily News Fetch

echo ============================================================
echo  COMPOUND.OS Daily AI News - Remove task
echo ============================================================
echo.
echo Task name: %TASK_NAME%
echo.

schtasks /Delete /TN "%TASK_NAME%" /F

if errorlevel 1 (
    echo.
    echo Task does not exist or removal failed.
    pause
    exit /b 1
)

echo.
echo OK: Daily task removed.
echo.
pause
endlocal

@echo off
chcp 65001
echo ========================================================
echo Politics News Watcher System - Daily Backup Tool
echo ========================================================

set "SOURCE_DIR=F:\Politics_News_Watcher"
set "DEST_DIR=H:\マイドライブ\Politics_News_Watcher_Assets"

echo Source: %SOURCE_DIR%
echo Dest  : %DEST_DIR%
echo.

if not exist "%DEST_DIR%" (
    echo Destination not found. Creating...
    mkdir "%DEST_DIR%"
)

echo Starting Robocopy Mirror...
echo.

rem /MIR: Mirror directory tree (Copy new/changed, delete extra in dest)
rem /XO: Exclude Older (Don't overwrite newer files in dest if exists)
rem /XD: Exclude Directories (.git, venv, pycache)
rem /XF: Exclude Files (*.pyc)
rem /R:3 /W:5: Retry 3 times, wait 5 sec on error

robocopy "%SOURCE_DIR%" "%DEST_DIR%" /MIR /XO /XD .git .github __pycache__ venv /XF *.pyc /R:3 /W:5 /NP /TEE /LOG+:F:\Politics_News_Watcher\backup_log.txt

if %ERRORLEVEL% LSS 8 (
    echo.
    echo Backup Completed Successfully.
) else (
    echo.
    echo Backup Completed with ERRORS. Check backup_log.txt.
)

echo.
timeout /t 10

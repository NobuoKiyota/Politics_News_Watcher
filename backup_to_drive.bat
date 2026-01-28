@echo off
chcp 65001
echo ========================================================
echo Politics News Watcher System - Daily Backup Tool
echo ========================================================

set "SOURCE_DIR=F:\Politics_News_Watcher"
set "DEST_DIR=J:\マイドライブ\Politics_News_Watcher_Assets"

echo Source: %SOURCE_DIR%
echo Dest  : %DEST_DIR%
echo.

if not exist "%DEST_DIR%" (
    echo Destination not found. Creating...
    mkdir "%DEST_DIR%"
)

echo Starting Robocopy Mirror...
echo.

rem /MIR: Mirror directory tree
rem /XO: Exclude Older
rem /XD: Exclude Directories (.git, venv, pycache)
rem /XF: Exclude Files (*.pyc)
rem /R:3 /W:5: Retry settings
rem /COPY:DT: Copy Data and Time only (Skip Attributes to avoid "FileSystem" errors on GDrive)
rem /FFT: Use FAT File Time (2-second granularity) for compatibility

robocopy "%SOURCE_DIR%" "%DEST_DIR%" /MIR /XO /XD .git .github __pycache__ venv .venv /XF *.pyc /R:3 /W:5 /NP /TEE /COPY:DT /FFT /LOG+:F:\Politics_News_Watcher\backup_log.txt

if %ERRORLEVEL% LSS 8 (
    echo.
    echo Backup Completed Successfully.
) else (
    echo.
    echo Backup Completed with ERRORS. Check backup_log.txt.
)

echo.
timeout /t 10

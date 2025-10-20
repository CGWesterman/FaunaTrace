@echo off
echo Starting Waypoint-Video Correlator GUI...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    pause
    exit /b 1
)

REM Launch the GUI
python launch_gui.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo An error occurred. Check the messages above.
    pause
)
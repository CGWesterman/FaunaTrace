#!/bin/bash

echo "Starting Waypoint-Video Correlator GUI..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        echo "Please install Python 3.6+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Launch the GUI
$PYTHON_CMD launch_gui.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "An error occurred. Check the messages above."
    read -p "Press Enter to continue..."
fi
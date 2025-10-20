#!/usr/bin/env python3
"""
Launcher script for the Waypoint-Video Correlator GUI

This script provides an easy way to launch the GUI application
and includes some basic system checks.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox


def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import tkinter
        print("✓ tkinter is available")
    except ImportError:
        print("✗ tkinter is not available")
        return False
    
    try:
        from waypoint_video_correlator import WaypointVideoCorrelator
        print("✓ waypoint_video_correlator module is available")
    except ImportError as e:
        print(f"✗ waypoint_video_correlator module not found: {e}")
        return False
    
    return True


def check_ffmpeg():
    """Check if ffmpeg/ffprobe is available."""
    import subprocess
    try:
        result = subprocess.run(['ffprobe', '-version'], 
                              capture_output=True, check=True)
        print("✓ ffprobe is available (enhanced video metadata extraction)")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ ffprobe not found (will use file system fallback for video metadata)")
        return False


def main():
    """Main launcher function."""
    print("Waypoint-Video Correlator GUI Launcher")
    print("=" * 40)
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("\n❌ Missing required dependencies!")
        print("Please ensure you have:")
        print("- Python 3.6+ with tkinter")
        print("- waypoint_video_correlator.py in the same directory")
        input("\nPress Enter to exit...")
        return 1
    
    # Check ffmpeg
    print("\nChecking optional dependencies...")
    check_ffmpeg()
    
    # Launch GUI
    print("\n🚀 Launching GUI...")
    try:
        from waypoint_video_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"\n❌ Error launching GUI: {e}")
        input("Press Enter to exit...")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
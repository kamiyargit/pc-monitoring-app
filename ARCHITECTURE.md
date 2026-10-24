# Architecture

## Stack
- Python 3.x
- Standard library modules (os, sys, subprocess, etc.)
- PySide6 for GUI
- PyInstaller for executable creation
- pyqtgraph for chart visualization

## Folder Structure
- monitoring_app.py - Main application logic with GUI
- ping_worker.py - Ping functionality in background thread
- system_info.py - System information gathering
- create_exe.py - Executable creation script
- ARCHITECTURE.md - This file
- NOTES.md - Project status and notes
- requirements.txt - Project dependencies

## Main Modules
1. monitoring_app.py - Main GUI and control flow with logging
2. ping_worker.py - Background ping operations with threading
3. system_info.py - System information retrieval
4. create_exe.py - Executable packaging

## Key Decisions
- Using PySide6 for rich GUI instead of tkinter
- Using pyqtgraph for chart visualization
- Comprehensive logging throughout the application
- Data persistence using JSON files for targets
- Background threading for ping operations to prevent UI blocking
- Ping subprocesses run hidden on Windows via `creationflags=CREATE_NO_WINDOW`
  (in `ping_worker.py`) so no CMD window flashes on each check
# PC Monitoring Application

A Windows desktop application for monitoring system information and network ping latency using PySide6, pyqtgraph, and psutil.

## Features

- Real-time system information display (CPU, RAM, OS, uptime)
- Network ping monitoring with live charting
- Per-target ping status panel (current latency and up/down status)
- Dark theme UI for comfortable viewing
- Configurable ping targets and update intervals
- Persistent target list — targets are saved to `targets.json` and restored on startup
- Application logging to `monitoring_app.log` and the console
- Ping subprocesses run hidden on Windows (no flashing CMD window)
- Optional: package as a standalone Windows executable with PyInstaller
- Multi-platform support (Windows, macOS, Linux)

## Requirements

- Python 3.7+
- PySide6
- pyqtgraph
- psutil

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python monitoring_app.py
```

### Features:

1. **System Information**: Displays real-time system information including CPU usage, RAM usage, OS details, and uptime.

2. **Ping Targets**:
   - Add ping targets by entering IP addresses or hostnames
   - Remove targets using the "Remove Selected" button
   - Choose update interval (1 second or 5 seconds)

3. **Live Charting**:
   - Real-time visualization of ping latency over time
   - Color-coded lines for different targets
   - Automatic data point management to prevent memory issues

4. **Ping Status Panel**:
   - Scrollable list showing each target's current ping and status
   - Updates automatically with the selected interval

5. **Persistence & Logging**:
   - Target list saved to `targets.json` and reloaded on startup
   - Application events logged to `monitoring_app.log`

## Building the Executable (Windows)

```
python create_exe.py
```

This installs PyInstaller if needed and builds a single-file, windowed
`PC_Monitoring_App.exe` in the `dist/` folder.

## Files

- `monitoring_app.py` - Main application window and UI logic
- `system_info.py` - System information gathering functions
- `ping_worker.py` - Ping operations in a separate thread
- `create_exe.py` - PyInstaller build script
- `monitoring_app.spec` - PyInstaller spec file
- `test_app.py` / `final_test.py` - Application smoke tests
- `targets.json` - Persisted ping targets (created at runtime)
- `requirements.txt` - Required Python packages

## License

This project is licensed under the MIT License.
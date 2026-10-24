# PC Monitoring Application

A Windows desktop application for monitoring system information and network ping latency using PySide6, pyqtgraph, and psutil.

## Features

- Real-time system information display (CPU, RAM, OS, uptime)
- Network ping monitoring with live charting
- Dark theme UI for comfortable viewing
- Configurable ping targets and update intervals
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

## Files

- `monitoring_app.py` - Main application window and UI logic
- `system_info.py` - System information gathering functions
- `ping_worker.py` - Ping operations in a separate thread
- `requirements.txt` - Required Python packages

## License

This project is licensed under the MIT License.
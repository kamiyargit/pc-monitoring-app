import socket
import subprocess
import sys
import time
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication

class PingWorker(QThread):
    """Worker thread for ping operations."""
    
    # Signals to communicate with main thread
    ping_result = Signal(str, float, bool)  # target, latency, success
    error = Signal(str, str)  # operation, error_message
    
    def __init__(self):
        super().__init__()
        self.targets = []
        self.is_running = False
        self.interval = 1000  # Default 1 second in milliseconds
        
    def set_targets(self, targets):
        """Set ping targets."""
        self.targets = targets.copy()
        
    def set_interval(self, interval_ms):
        """Set update interval in milliseconds."""
        self.interval = interval_ms
        
    def run(self):
        """Main thread loop for pinging targets."""
        self.is_running = True
        
        while self.is_running:
            # Ping all targets
            for target in self.targets:
                if not self.is_running:
                    break
                    
                latency, success = self.ping_target(target)
                self.ping_result.emit(target, latency, success)
                
            # Wait before next ping cycle
            self.msleep(self.interval)
            
    def ping_target(self, target):
        """Ping a single target and return latency and success status."""
        try:
            # Validate target is not empty
            if not target or not target.strip():
                return -1, False
                
            # Use different approach based on OS
            if sys.platform == "win32":
                # Windows ping command
                cmd = ["ping", "-n", "1", "-w", "1000", target]
                try:
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=2,
                        check=True
                    )
                    # Parse the output to get latency
                    output = result.stdout.decode('utf-8')
                    if "time=" in output:
                        time_str = output.split("time=")[1].split("ms")[0]
                        latency = float(time_str)
                        return latency, True
                    else:
                        return -1, False
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
                    # If ping fails or parsing fails, return timeout
                    return -1, False
                    
            else:
                # Unix/Linux ping command
                cmd = ["ping", "-c", "1", "-W", "1", target]
                try:
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=2,
                        check=True
                    )
                    output = result.stdout.decode('utf-8')
                    if "time=" in output:
                        time_str = output.split("time=")[1].split("ms")[0]
                        latency = float(time_str)
                        return latency, True
                    else:
                        return -1, False
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
                    return -1, False
                    
        except Exception as e:
            self.error.emit(target, str(e))
            return -1, False
            
    def stop(self):
        """Stop the ping worker."""
        self.is_running = False
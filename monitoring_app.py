import sys
import socket
import json
import os
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                              QListWidget, QGroupBox, QComboBox, QScrollArea)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import pyqtgraph as pg
from system_info import get_formatted_system_info
from ping_worker import PingWorker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitoringApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Monitoring Application")
        self.setGeometry(100, 100, 1000, 800)
        
        # Initialize ping worker
        self.ping_worker = PingWorker()
        self.ping_worker.ping_result.connect(self.handle_ping_result)
        self.ping_worker.error.connect(self.handle_ping_error)
        self.ping_worker.start()
        
        # Initialize logging (already configured at the top)
        
        # Initialize UI
        self.init_ui()
        
        # Load saved targets on startup
        self.load_targets()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 4px;
            }
            QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QGroupBox {
                background-color: #252525;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                left: 10px;
                color: #ffffff;
            }
        """)
        
        # System info section
        system_group = QGroupBox("System Information")
        system_layout = QVBoxLayout()
        self.system_label = QLabel()
        self.system_label.setWordWrap(True)
        system_layout.addWidget(self.system_label)
        system_group.setLayout(system_layout)
        main_layout.addWidget(system_group)
        
        # Update system info immediately
        self.update_system_info()
        
        # Ping targets section
        targets_group = QGroupBox("Ping Targets")
        targets_layout = QVBoxLayout()
        
        # Input and buttons
        input_layout = QHBoxLayout()
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter IP address or hostname...")
        add_button = QPushButton("Add Target")
        add_button.clicked.connect(self.add_target)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_target)
        
        input_layout.addWidget(self.target_input)
        input_layout.addWidget(add_button)
        input_layout.addWidget(remove_button)
        targets_layout.addLayout(input_layout)
        
        # Targets list
        self.targets_list = QListWidget()
        self.targets_list.setSelectionMode(QListWidget.SingleSelection)
        targets_layout.addWidget(self.targets_list)
        
        # Interval selection
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Update Interval:")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1 second", "5 seconds"])
        self.interval_combo.setCurrentText("1 second")
        self.interval_combo.currentTextChanged.connect(self.update_interval)
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_combo)
        interval_layout.addStretch()
        targets_layout.addLayout(interval_layout)
        
        targets_group.setLayout(targets_layout)
        main_layout.addWidget(targets_group)
        
        # Ping status display section
        status_group = QGroupBox("Ping Status")
        status_layout = QVBoxLayout()
        
        # Create a container for individual target status displays
        self.status_container = QWidget()
        self.status_layout = QVBoxLayout(self.status_container)
        self.status_layout.setSpacing(5)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add scroll area to handle many targets
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.status_container)
        
        status_layout.addWidget(scroll_area)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Set initial size
        self.resize(800, 600)
        
    def add_target(self):
        """Add a new ping target."""
        target = self.target_input.text().strip()
        if not target:
            logger.warning("Empty target entered")
            return
            
        # Validate target (basic validation)
        if not self.is_valid_target(target):
            logger.warning(f"Invalid target format: {target}")
            return
            
        # Check if already in list
        for i in range(self.targets_list.count()):
            if self.targets_list.item(i).text() == target:
                logger.warning(f"Target {target} already exists")
                return
                
        # Add to list
        self.targets_list.addItem(target)
        
        # Update worker targets
        self.update_worker_targets()
        
        # Save targets after adding
        self.save_targets()
        
        # Clear input
        self.target_input.clear()
        
        logger.info(f"Added target: {target}")
        
    def remove_target(self):
        """Remove selected ping target."""
        current_item = self.targets_list.currentItem()
        if current_item:
            self.targets_list.takeItem(self.targets_list.row(current_item))
            self.update_worker_targets()
            # Save targets after removal
            self.save_targets()
            logger.info(f"Removed target: {current_item.text()}")
            
    def is_valid_target(self, target):
        """Validate a target (hostname or IP address)."""
        # Basic validation - check if it's not empty
        if not target or not target.strip():
            logger.warning("Empty target detected")
            return False
            
        # Try to resolve the hostname (basic check)
        try:
            # Test if it's a valid IP address format or hostname
            socket.getaddrinfo(target, None)
            return True
        except socket.gaierror:
            # If we can't resolve it, it might still be a valid target for ping
            # We'll allow it to pass through and let the ping operation handle it
            logger.debug(f"Could not resolve {target}, but allowing ping attempt")
            return True
            
    def save_targets(self):
        """Save targets to a file."""
        try:
            targets = []
            for i in range(self.targets_list.count()):
                targets.append(self.targets_list.item(i).text())
            
            # Save to JSON file
            with open('targets.json', 'w') as f:
                json.dump(targets, f)
            logger.info(f"Saved {len(targets)} targets to file")
        except Exception as e:
            logger.error(f"Error saving targets: {e}")
            
    def load_targets(self):
        """Load targets from a file."""
        try:
            if os.path.exists('targets.json'):
                with open('targets.json', 'r') as f:
                    targets = json.load(f)
                
                # Add loaded targets to the list
                for target in targets:
                    if target not in [self.targets_list.item(i).text() for i in range(self.targets_list.count())]:
                        self.targets_list.addItem(target)
                
                # Update ping worker with loaded targets
                self.update_worker_targets()
                logger.info(f"Loaded {len(targets)} targets from file")
        except Exception as e:
            logger.error(f"Error loading targets: {e}")
            
    def update_worker_targets(self):
        """Update targets in ping worker."""
        targets = []
        for i in range(self.targets_list.count()):
            targets.append(self.targets_list.item(i).text())
            
        self.ping_worker.set_targets(targets)
        
    def update_interval(self, text):
        """Update ping interval based on selection."""
        if text == "1 second":
            interval = 1000
        else:  # 5 seconds
            interval = 5000
            
        self.ping_worker.set_interval(interval)
        logger.info(f"Update interval set to {text}")
        
    def handle_ping_result(self, target, latency, success):
        """Handle ping result from worker thread."""
        # Update status display instead of chart
        self.update_target_status(target, latency, success)
        
    def handle_ping_error(self, target, error_message):
        """Handle ping errors."""
        logger.error(f"Error pinging {target}: {error_message}")
        # Even in case of error, we should update the status display
        self.update_target_status(target, -1, False)
        
    def update_target_status(self, target, latency, success):
        """Update the status display for a specific target."""
        # Find or create the status widget for this target
        target_widget = None
        for i in range(self.status_layout.count()):
            item = self.status_layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                # Check if this is the widget for our target
                if hasattr(widget, 'target') and widget.target == target:
                    target_widget = widget
                    break
        
        # If we don't have a widget for this target yet, create one
        if not target_widget:
            target_widget = self.create_target_status_widget(target)
            self.status_layout.addWidget(target_widget)
        
        # Update the status information in the widget
        if success and latency >= 0:
            # Format ping value with TTL if available
            ping_value = f"{latency:.1f} ms"
            status_text = "stable"
            status_color = "#4CAF50"  # Green
            
            if 99 <= latency < 150:
                status_text = "unstable"
                status_color = "#FFC107"  # Orange
            elif latency >= 150:
                status_text = "awful!"
                status_color = "#FF5252"  # Red
                
            target_widget.findChild(QLabel, "ping_label").setText(f"Current ping: {ping_value}")
            target_widget.findChild(QLabel, "status_label").setText(f"Status: {status_text}")
            target_widget.findChild(QLabel, "status_label").setStyleSheet(f"color: {status_color}; font-weight: bold;")
        else:
            target_widget.findChild(QLabel, "ping_label").setText("Current ping: Error")
            target_widget.findChild(QLabel, "status_label").setText("Status: Offline")
            target_widget.findChild(QLabel, "status_label").setStyleSheet("color: #FF5252; font-weight: bold;")
    
    def create_target_status_widget(self, target):
        """Create a widget to display status for a single target."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Target label
        target_label = QLabel(f"IP: {target}")
        target_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(target_label)
        
        # Ping value label
        ping_label = QLabel("Current ping: Waiting...")
        ping_label.setObjectName("ping_label")
        layout.addWidget(ping_label)
        
        # Status label
        status_label = QLabel("Status: Waiting...")
        status_label.setObjectName("status_label")
        layout.addWidget(status_label)
        
        # Store target info in widget for later reference
        widget.target = target
        
        return widget
        
    def update_system_info(self):
        """Update system information display."""
        try:
            info_text = get_formatted_system_info()
            self.system_label.setText(info_text)
            logger.debug("System information updated")
        except Exception as e:
            self.system_label.setText(f"Error fetching system info: {str(e)}")
            logger.error(f"Error fetching system info: {e}")
            
    def closeEvent(self, event):
        """Handle application closing."""
        # Save targets before closing
        self.save_targets()
        
        # Stop ping worker
        self.ping_worker.stop()
        self.ping_worker.wait()
        logger.info("Application closed")
        event.accept()

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("PC Monitoring Application")
    
    window = MonitoringApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
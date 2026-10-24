import sys
import socket
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QListWidget, QGroupBox, QComboBox)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import pyqtgraph as pg
from system_info import get_formatted_system_info
from ping_worker import PingWorker

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
        
        # Initialize chart data storage
        self.ping_data = {}
        
        # Initialize UI
        self.init_ui()
        
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
                subline-offset: -10;
                left: 10px;
                color: #ffffff;
            }
        """)
        
        # System info section
        system_group = QGroupBox("System Information")
        system_layout = QVBoxLayout()
        self.system_label = QLabel()
        self.system_label.setWordWrap(True)
        self.system_label.setFont(QFont("Consolas", 10))
        system_layout.addWidget(self.system_label)
        system_group.setLayout(system_layout)
        main_layout.addWidget(system_group)
        
        # Ping targets section
        ping_group = QGroupBox("Ping Targets")
        ping_layout = QVBoxLayout()
        
        # Input and controls
        input_layout = QHBoxLayout()
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter IP address or hostname (e.g. 8.8.8.8)")
        self.target_input.returnPressed.connect(self.add_target)
        
        add_button = QPushButton("Add Target")
        add_button.clicked.connect(self.add_target)
        
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_target)
        
        input_layout.addWidget(self.target_input)
        input_layout.addWidget(add_button)
        input_layout.addWidget(remove_button)
        
        # Ping targets list
        self.targets_list = QListWidget()
        self.targets_list.setMinimumHeight(100)
        
        # Update interval selector
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Update Interval:")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1 second", "5 seconds"])
        self.interval_combo.setCurrentIndex(0)  # Default to 1 second
        self.interval_combo.currentTextChanged.connect(self.update_interval)
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_combo)
        interval_layout.addStretch()
        
        ping_layout.addLayout(input_layout)
        ping_layout.addWidget(self.targets_list)
        ping_layout.addLayout(interval_layout)
        ping_group.setLayout(ping_layout)
        main_layout.addWidget(ping_group)
        
        # Chart section
        chart_group = QGroupBox("Ping Latency Chart")
        chart_layout = QVBoxLayout()
        
        # Create pyqtgraph plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1e1e1e')
        self.plot_widget.setTitle("Ping Latency Over Time", color='w', size='14pt')
        self.plot_widget.setLabel('left', 'Latency (ms)', color='w')
        self.plot_widget.setLabel('bottom', 'Time', color='w')
        self.plot_widget.showGrid(x=True, y=True)
        
        # Set plot colors
        axis = self.plot_widget.getAxis('left')
        axis.setPen('#ffffff')
        axis.setTextPen('#ffffff')
        axis = self.plot_widget.getAxis('bottom')
        axis.setPen('#ffffff')
        axis.setTextPen('#ffffff')
        
        chart_layout.addWidget(self.plot_widget)
        chart_group.setLayout(chart_layout)
        main_layout.addWidget(chart_group)
        
        # Initial system info update
        self.update_system_info()
        
    def add_target(self):
        """Add a new ping target."""
        target = self.target_input.text().strip()
        if not target:
            return
            
        # Validate target (basic validation)
        if not self.is_valid_target(target):
            return
            
        # Check if already in list
        for i in range(self.targets_list.count()):
            if self.targets_list.item(i).text() == target:
                return
                
        # Add to list
        self.targets_list.addItem(target)
        
        # Update worker targets
        self.update_worker_targets()
        
        # Clear input
        self.target_input.clear()
        
    def remove_target(self):
        """Remove selected ping target."""
        current_item = self.targets_list.currentItem()
        if current_item:
            self.targets_list.takeItem(self.targets_list.row(current_item))
            self.update_worker_targets()
            
    def is_valid_target(self, target):
        """Validate a target (hostname or IP address)."""
        # Basic validation - check if it's not empty
        if not target or not target.strip():
            return False
            
        # Try to resolve the hostname (basic check)
        try:
            # Test if it's a valid IP address format or hostname
            socket.getaddrinfo(target, None)
            return True
        except socket.gaierror:
            # If we can't resolve it, it might still be a valid target for ping
            # We'll allow it to pass through and let the ping operation handle it
            return True
            
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
        
    def handle_ping_result(self, target, latency, success):
        """Handle ping result from worker thread."""
        # Update chart with new data point
        self.update_chart_data(target, latency, success)
        
    def handle_ping_error(self, target, error_message):
        """Handle ping errors."""
        print(f"Error pinging {target}: {error_message}")
        
    def update_chart_data(self, target, latency, success):
        """Update chart with new ping data."""
        # Initialize data for this target if needed
        if target not in self.ping_data:
            self.ping_data[target] = []
            
        # Add new data point (timestamp, latency)
        current_time = len(self.ping_data[target])
        self.ping_data[target].append((current_time, latency))
        
        # Keep only last 50 points to prevent memory issues
        if len(self.ping_data[target]) > 50:
            self.ping_data[target] = self.ping_data[target][-50:]
            
        # Update chart (this will be done in a separate update method)
        self.update_chart()
        
    def update_chart(self):
        """Update the chart with current data."""
        # Clear existing plots
        self.plot_widget.clear()
        
        # Plot each target's data
        colors = ['#FF5252', '#4CAF50', '#2196F3', '#FFC107', '#9C27B0']
        
        for i, (target, data) in enumerate(self.ping_data.items()):
            if not data:
                continue
                
            # Extract x and y values
            x_values = [point[0] for point in data]
            y_values = [point[1] for point in data]
            
            # Plot with color
            self.plot_widget.plot(
                x_values, 
                y_values, 
                pen=pg.mkPen(color=colors[i % len(colors)], width=2),
                name=target,
                symbol='o',
                symbolSize=5
            )
            
        # Set plot title and labels
        self.plot_widget.setTitle("Ping Latency Over Time", color='w', size='14pt')
        
    def update_system_info(self):
        """Update system information display."""
        try:
            info_text = get_formatted_system_info()
            self.system_label.setText(info_text)
        except Exception as e:
            self.system_label.setText(f"Error fetching system info: {str(e)}")
            
    def closeEvent(self, event):
        """Handle application closing."""
        # Stop ping worker
        self.ping_worker.stop()
        self.ping_worker.wait()
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
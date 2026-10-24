#!/usr/bin/env python3
"""
Test script for ping monitoring application.
This script verifies that the application starts correctly with the new UI design.
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from monitoring_app import MonitoringApp

def test_application():
    """Test that the application starts correctly."""
    print("Starting ping monitoring application test...")
    
    try:
        # Create QApplication instance
        app = QApplication(sys.argv)
        
        # Create main window
        window = MonitoringApp()
        
        # Show window
        window.show()
        
        print("Application started successfully!")
        print("UI elements created:")
        print("- System information section")
        print("- Ping targets section with input and list")
        print("- Ping status section with scrollable display")
        
        # Test that the new UI components exist
        assert hasattr(window, 'status_container'), "Status container not found"
        assert hasattr(window, 'status_layout'), "Status layout not found"
        assert hasattr(window, 'targets_list'), "Targets list not found"
        print("All UI components present!")
        
        return True
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_application()
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!")
        sys.exit(1)
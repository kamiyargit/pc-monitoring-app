import subprocess
import sys
import os

def create_executable():
    try:
        # Change to project directory
        project_dir = r'e:\test-local-AI\ping-monitoring'
        os.chdir(project_dir)
        
        # Install pyinstaller if not already installed
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        
        # Create the executable
        print("Creating executable...")
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            'monitoring_app.py'
        ])
        
        print("Executable created successfully!")
        print("Check the 'dist' folder for your PC_Monitoring_App.exe file")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    create_executable()
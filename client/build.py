import os
import shutil
import subprocess
import sys

def build_exe():
    """
    Build the client application into a single executable using PyInstaller
    and place it in the parent directory.
    """
    # Ensure we're in the client directory
    client_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(client_dir)
    
    # Ensure PyInstaller is installed
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install PyInstaller")
        return False
    
    # Build executable
    print("Building executable with PyInstaller...")
    
    # Define the PyInstaller command with necessary options
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                   # Create a single executable file
        "--windowed",                  # No console window for Windows
        "--icon=icon.ico",            # Set application icon
        "--name=DWAutoSync",          # Name of the executable
        "--add-data=icon.ico;.",      # Include the icon file
        "--add-data=icon.png;.",      # Include the icon PNG file
        "main.py"                     # Main script
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("PyInstaller build completed successfully.")
    except subprocess.CalledProcessError:
        print("PyInstaller build failed")
        return False
    
    # Move the executable to the parent directory
    parent_dir = os.path.dirname(client_dir)
    dist_dir = os.path.join(client_dir, "dist")
    
    if os.path.exists(dist_dir):
        # Get the executable name (should be DWAutoSync.exe on Windows)
        exe_file = [f for f in os.listdir(dist_dir) if f.endswith('.exe')][0]
        exe_path = os.path.join(dist_dir, exe_file)
        
        # Move executable to parent directory
        dest_path = os.path.join(parent_dir, exe_file)
        shutil.copy2(exe_path, dest_path)
        print(f"Executable copied to: {dest_path}")
        
        # Cleanup build artifacts
        shutil.rmtree(os.path.join(client_dir, "build"), ignore_errors=True)
        shutil.rmtree(dist_dir, ignore_errors=True)
        spec_file = os.path.join(client_dir, "DWAutoSync.spec")
        if os.path.exists(spec_file):
            os.remove(spec_file)
        print("Build artifacts cleaned up.")
        
        return True
    else:
        print("Dist directory not found")
        return False

if __name__ == "__main__":
    if build_exe():
        print("Build completed successfully!")
    else:
        print("Build failed!")
        sys.exit(1) 
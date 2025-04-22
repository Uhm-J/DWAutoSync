# worker.py
# Defines the Worker class for handling background monitoring and uploads.

import os
import sys
import time
import requests
import psutil
import pathlib

# --- PyQt5 Imports ---
# Use QtCore only, as this shouldn't interact directly with Widgets
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

# --- Local Imports ---
import config # Import constants from config.py

class Worker(QObject):
    """
    Runs the monitoring task in a separate thread.
    Emits signals to update the GUI safely.
    """
    log_message = pyqtSignal(str) # Signal to send log messages
    process_status_changed = pyqtSignal(bool) # Signal for process status (running T/F)

    def __init__(self):
        super().__init__()
        self._is_running = True
        self._was_process_running = False
        self._last_modified_time = None  # Track last modified time of save file

    def reload_config(self):
        """Reload configuration after settings have changed."""
        # We'll reload the config module which will reload settings from the JSON file
        import importlib
        import config
        importlib.reload(config)
        self.log_message.emit("Worker configuration reloaded.")

    def stop(self):
        """Signals the worker loop to terminate."""
        self._is_running = False
        self.log_message.emit("Stop signal received by worker.")

    def find_process(self, name):
        """Check if a process with the given name is running."""
        try:
            for proc in psutil.process_iter(['name']):
                # Use case-insensitive comparison for process names if needed
                if proc.info['name'].lower() == name.lower():
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Ignore processes that ended or we can't access
            pass
        except Exception as e:
            self.log_message.emit(f"[Error] Failed to check processes: {e}")
        return False

    def get_save_file_path(self):
        """Construct the full path to the save file using config."""
        try:
            if sys.platform == "win32":
                # Use %APPDATA% environment variable which usually points to Roaming
                base_path = pathlib.Path(os.getenv('APPDATA', ''))
                base_path = base_path.parent  # Strip last directory
                base_path = base_path / "Local"  # Add "Local" directory
                self.log_message.emit(f"[Debug] Using APPDATA: {base_path}")
            else:
                # Use ~/.config as a common base for Linux/macOS
                base_path = pathlib.Path.home() / ".config"

            if not base_path or not os.path.isdir(base_path):
                 # Fallback to home directory if standard config dirs don't work
                 base_path = pathlib.Path.home()
                 self.log_message.emit(f"[Warning] Could not find standard config dir, using home: {base_path}")
                 # You might want a more specific fallback or error here

            if not base_path:
                raise ValueError("Could not determine a suitable base directory.")
            
            # Remove leading backslash if present to prevent creating an absolute path
            save_folder = config.SAVE_FOLDER_NAME.lstrip('\\/')
            
            # Don't include "Local" in the path as it doesn't appear in the expected path
            full_path = os.path.join(str(base_path), save_folder, config.SAVE_FILE_NAME)
            self.log_message.emit(f"[Debug] Using full path: {full_path}")
            return full_path
        except Exception as e:
            self.log_message.emit(f"[Error] Constructing save file path: {e}")
            return None

    def upload_file(self, file_path):
        """Uploads the specified file to the server using config."""

        if not file_path or not os.path.isfile(file_path):
            self.log_message.emit(f"[Error] Save file not found or is not a file: {file_path}")
            return

        self.log_message.emit(f"Attempting upload: {os.path.basename(file_path)}")
        try:
            with open(file_path, 'rb') as f:
                # 'savefile' is the form field name expected by the server
                file_data = {'savefile': (os.path.basename(file_path), f)}
                
                # Add user_name to the headers if available
                headers = {config.AUTH_HEADER_KEY: config.API_KEY}
                if config.USER_NAME:
                    headers['X-User-Name'] = config.USER_NAME
                
                self.log_message.emit(f"Connecting to server: {config.SERVER_UPLOAD_URL}")
                response = requests.post(
                    config.SERVER_UPLOAD_URL,
                    files=file_data,
                    headers=headers,
                    timeout=30 # Request timeout in seconds
                )
                # Raise HTTPError for bad responses (4xx or 5xx)
                response.raise_for_status()
                self.log_message.emit(f"Upload successful for {os.path.basename(file_path)}. Status: {response.status_code}")

        except FileNotFoundError:
            self.log_message.emit(f"[Error] Could not find file for upload: {file_path}")
        except requests.exceptions.Timeout:
             self.log_message.emit(f"[Error] Upload timed out for {os.path.basename(file_path)}.")
        except requests.exceptions.ConnectionError:
             self.log_message.emit(f"[Error] Could not connect to server at {config.SERVER_UPLOAD_URL}.")
        except requests.exceptions.HTTPError as e:
             self.log_message.emit(f"[Error] Upload failed (HTTP Status {e.response.status_code}): {e.response.text[:200]}") # Show beginning of error response
        except requests.exceptions.RequestException as e:
            self.log_message.emit(f"[Error] General upload request failed: {e}")
        except Exception as e:
            self.log_message.emit(f"[Error] Unexpected upload error: {e}")

    def ping_server(self):
        """Ping the server and display the response."""
        try:
            response = requests.get(config.SERVER_URL + "/api/status", headers={config.AUTH_HEADER_KEY: config.API_KEY})
            self.log_message.emit(f"Server response: {response.text}")
        except Exception as e:
            self.log_message.emit(f"[Error] Failed to ping server: {e}")

    def force_upload_save(self):
        """Force upload the save file."""
        save_path = self.get_save_file_path()
        if save_path:
            # Update the last modified time when manually uploading
            if os.path.exists(save_path):
                self._last_modified_time = self.get_file_modified_time(save_path)
            self.upload_file(save_path)
        else:
            self.log_message.emit(f"[Error] Could not find save file at {save_path}")

    def download_latest_save(self):
        """Download the latest save file from the server."""
        headers = {config.AUTH_HEADER_KEY: config.API_KEY, "save_file_name": config.SAVE_FILE_NAME}
        try:
            response = requests.get(config.SERVER_URL + "/api/download-latest", headers=headers)
            # self.log_message.emit(f"Server response: {response.text}")
            # self.log_message.emit(f"Downloading latest save file to {self.get_save_file_path()}")
            self.save_latest_save(self.get_save_file_path(), response.content)
        except Exception as e:
            self.log_message.emit(f"[Error] Failed to download latest save: {e}")

    def save_latest_save(self, file_path, response_content):
        """Save the latest save file to the local directory."""
        # First rename the existing save file to a backup name
        # file name as pathlib path
        file_path = pathlib.Path(file_path)
        if not os.path.exists(file_path):
            self.log_message.emit(f"[Error] Save file not found: {file_path}")
            with open(file_path, 'wb') as f:
                f.write(response_content)
            self.log_message.emit(f"Latest save file saved to {file_path}")
            return
        self.log_message.emit(f"Saving latest save file to {file_path}")
        backup_path = file_path.with_suffix('.bak')
        self.log_message.emit(f"Backup path: {backup_path}")
        if os.path.exists(backup_path):
            self.log_message.emit(f"Removing existing backup file: {backup_path}")
            os.remove(backup_path)
        self.log_message.emit(f"Renaming existing save file to backup: {file_path} -> {backup_path}")
        os.rename(file_path, backup_path)
        self.log_message.emit(f"Copying new save file to {file_path}")
        with open(file_path, 'wb') as f:
            f.write(response_content)
        self.log_message.emit(f"Latest save file saved to {file_path}")

    def get_file_modified_time(self, file_path):
        """Get the last modified time of a file."""
        try:
            if os.path.exists(file_path):
                return os.path.getmtime(file_path)
            return None
        except Exception as e:
            self.log_message.emit(f"[Error] Failed to get file modified time: {e}")
            return None

    def has_file_been_modified(self, file_path):
        """Check if the file has been modified since last upload."""
        if not file_path or not os.path.exists(file_path):
            return False
            
        current_mtime = self.get_file_modified_time(file_path)
        if current_mtime is None:
            return False
            
        # If we haven't checked before, consider it modified
        if self._last_modified_time is None:
            self._last_modified_time = current_mtime
            return True
            
        # Check if modified time has changed
        if current_mtime > self._last_modified_time:
            self.log_message.emit(f"Save file has been modified since last check.")
            self._last_modified_time = current_mtime
            return True
            
        return False

    @pyqtSlot()
    def run_monitoring_loop(self):
        """The main monitoring loop. Runs until stop() is called."""
        self.log_message.emit("Monitoring thread started.")
        try:
            # Perform initial check
            self._was_process_running = self.find_process(config.TARGET_PROCESS_NAME)
            self.log_message.emit(f"Initial state: {config.TARGET_PROCESS_NAME} is {'running' if self._was_process_running else 'not running'}.")
            self.process_status_changed.emit(self._was_process_running)
            
            # Get initial modified time of save file
            save_path = self.get_save_file_path()
            if save_path and os.path.exists(save_path):
                self._last_modified_time = self.get_file_modified_time(save_path)
                self.log_message.emit(f"Initial save file timestamp recorded.")
                
        except Exception as e:
            self.log_message.emit(f"[Error] During initial process check: {e}")

        while self._is_running:
            try:
                is_running_now = self.find_process(config.TARGET_PROCESS_NAME)

                # Check if status has changed since last poll
                if is_running_now != self._was_process_running:
                    status_msg = f"Status change: {config.TARGET_PROCESS_NAME} is now {'running' if is_running_now else 'not running'}."
                    self.log_message.emit(status_msg)
                    self.process_status_changed.emit(is_running_now)

                    # If process changed from running to stopped, check if save file was modified
                    if self._was_process_running and not is_running_now:
                        self.log_message.emit(f"Detected '{config.TARGET_PROCESS_NAME}' closed.")
                        save_path = self.get_save_file_path()
                        if save_path and self.has_file_been_modified(save_path):
                            self.log_message.emit("Save file was modified. Starting upload...")
                            self.upload_file(save_path)  # Perform the upload
                        else:
                            self.log_message.emit("Save file was not modified. Skipping upload.")

                    # Update the tracked state
                    self._was_process_running = is_running_now

            except Exception as e:
                self.log_message.emit(f"[Error] In monitoring cycle: {e}")
                # Avoid continuous error spamming if find_process fails repeatedly
                time.sleep(config.POLLING_INTERVAL_SECONDS * 2) # Longer sleep on error

            # Wait before the next check
            # Use a loop for sleeping to check _is_running more frequently
            # This allows the thread to stop faster when stop() is called.
            for _ in range(config.POLLING_INTERVAL_SECONDS):
                 if not self._is_running:
                     break
                 time.sleep(1) # Sleep 1 second at a time

        self.log_message.emit("Monitoring thread finished.") 
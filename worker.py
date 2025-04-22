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
            else:
                # Use ~/.config as a common base for Linux/macOS
                base_path = pathlib.Path.home() / ".config"

            if not base_path or not base_path.is_dir():
                 # Fallback to home directory if standard config dirs don't work
                 base_path = pathlib.Path.home()
                 self.log_message.emit(f"[Warning] Could not find standard config dir, using home: {base_path}")
                 # You might want a more specific fallback or error here

            if not base_path:
                raise ValueError("Could not determine a suitable base directory.")

            full_path = base_path / config.SAVE_FOLDER_NAME / config.SAVE_FILE_NAME
            return full_path
        except Exception as e:
            self.log_message.emit(f"[Error] Constructing save file path: {e}")
            return None

    def upload_file(self, file_path):
        """Uploads the specified file to the server using config."""
        if not file_path or not file_path.is_file():
            self.log_message.emit(f"[Error] Save file not found or is not a file: {file_path}")
            return

        self.log_message.emit(f"Attempting upload: {file_path.name}")
        try:
            with open(file_path, 'rb') as f:
                # 'savefile' is the form field name expected by the server
                file_data = {'savefile': (file_path.name, f)}
                headers = {config.AUTH_HEADER_KEY: config.API_KEY}

                response = requests.post(
                    config.SERVER_UPLOAD_URL,
                    files=file_data,
                    headers=headers,
                    timeout=30 # Request timeout in seconds
                )
                # Raise HTTPError for bad responses (4xx or 5xx)
                response.raise_for_status()
                self.log_message.emit(f"Upload successful for {file_path.name}. Status: {response.status_code}")

        except FileNotFoundError:
            self.log_message.emit(f"[Error] Could not find file for upload: {file_path}")
        except requests.exceptions.Timeout:
             self.log_message.emit(f"[Error] Upload timed out for {file_path.name}.")
        except requests.exceptions.ConnectionError:
             self.log_message.emit(f"[Error] Could not connect to server at {config.SERVER_UPLOAD_URL}.")
        except requests.exceptions.HTTPError as e:
             self.log_message.emit(f"[Error] Upload failed (HTTP Status {e.response.status_code}): {e.response.text[:200]}") # Show beginning of error response
        except requests.exceptions.RequestException as e:
            self.log_message.emit(f"[Error] General upload request failed: {e}")
        except Exception as e:
            self.log_message.emit(f"[Error] Unexpected upload error: {e}")

    @pyqtSlot()
    def run_monitoring_loop(self):
        """The main monitoring loop. Runs until stop() is called."""
        self.log_message.emit("Monitoring thread started.")
        try:
            # Perform initial check
            self._was_process_running = self.find_process(config.TARGET_PROCESS_NAME)
            self.log_message.emit(f"Initial state: {config.TARGET_PROCESS_NAME} is {'running' if self._was_process_running else 'not running'}.")
            self.process_status_changed.emit(self._was_process_running)
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

                    # If process changed from running to stopped, trigger upload
                    if self._was_process_running and not is_running_now:
                        self.log_message.emit(f"Detected '{config.TARGET_PROCESS_NAME}' closed. Starting upload...")
                        save_path = self.get_save_file_path()
                        if save_path:
                            self.upload_file(save_path) # Perform the upload

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
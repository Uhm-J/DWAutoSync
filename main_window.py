# main_window.py
# Defines the MainWindow class for the application's GUI.

import sys
import time
import pathlib

# --- PyQt5 Imports ---
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QVBoxLayout, QWidget,
                             QSystemTrayIcon, QMenu, QAction, QApplication, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSlot, Qt
from PyQt5.QtGui import QIcon

# --- Local Imports ---
import config # Import constants
from worker import Worker # Import the background worker class

class MainWindow(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        # Set window icon from config
        if pathlib.Path(config.ICON_PATH).is_file():
            self.setWindowIcon(QIcon(config.ICON_PATH))
        else:
             print(f"Warning: Window icon file not found at {config.ICON_PATH}")
        self.resize(600, 400) # Set default window size

        # --- UI Elements ---
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True) # Make the log display read-only

        # Set up the central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.log_display)
        self.setCentralWidget(central_widget)

        # --- System Tray Icon Setup ---
        self.setup_tray_icon()

        # --- Worker Thread Setup ---
        self.setup_worker_thread()

        # --- Initial Log Message ---
        self.append_log("Application initialized.")
        if not pathlib.Path(config.ICON_PATH).is_file():
            self.append_log(f"[Warning] Tray icon file not found at: {config.ICON_PATH}")


    def setup_tray_icon(self):
        """Creates and configures the system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        # Set tray icon from config
        if pathlib.Path(config.ICON_PATH).is_file():
            self.tray_icon.setIcon(QIcon(config.ICON_PATH))
        else:
            # Optionally use a default Qt icon if main one is missing
            # self.tray_icon.setIcon(QApplication.style().standardIcon(QStyle.SP_ComputerIcon))
             print(f"Warning: Tray icon file not found at {config.ICON_PATH}")


        # Create context menu for the tray icon
        tray_menu = QMenu()
        show_action = QAction("Show Window", self)
        quit_action = QAction("Quit", self)

        # Connect actions to methods
        show_action.triggered.connect(self.show_window)
        quit_action.triggered.connect(self.quit_application) # Connect to custom quit method

        # Add actions to the menu
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show() # Make the tray icon visible

        # Connect tray icon activation signal (e.g., left-click)
        self.tray_icon.activated.connect(self.handle_tray_activation)

    def setup_worker_thread(self):
        """Initializes and starts the background worker thread."""
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread) # Move worker object to the thread

        # --- Connect Worker Signals to Main Window Slots ---
        # Connect log messages from worker to the append_log slot
        self.worker.log_message.connect(self.append_log)
        # Connect process status changes to update_status_indicator slot
        self.worker.process_status_changed.connect(self.update_status_indicator)
        # Connect the thread's started signal to the worker's main execution method
        self.thread.started.connect(self.worker.run_monitoring_loop)
        # Optional: Connect thread finished signal for cleanup if needed
        # self.thread.finished.connect(self.on_thread_finished)

        # Start the background thread
        self.thread.start()
        self.append_log("Worker thread initiated.")

    @pyqtSlot(str)
    def append_log(self, message):
        """Appends a formatted message to the log display text edit."""
        # Ensure this runs in the main GUI thread
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.log_display.append(f"{timestamp} - {message}")
        # Optional: Auto-scroll to the bottom
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())


    @pyqtSlot(bool)
    def update_status_indicator(self, is_running):
        """Updates the tray icon tooltip based on process status."""
        status_text = f"{config.TARGET_PROCESS_NAME} is {'running' if is_running else 'not running'}"
        tooltip = f"{config.APP_NAME}\n{status_text}"
        self.tray_icon.setToolTip(tooltip)
        # You could also change the tray icon itself here based on status
        # e.g., self.tray_icon.setIcon(QIcon('running_icon.png' if is_running else 'stopped_icon.png'))

    @pyqtSlot(QSystemTrayIcon.ActivationReason)
    def handle_tray_activation(self, reason):
        """Handles left-click activation on the tray icon to show/hide the window."""
        # QSystemTrayIcon.Trigger corresponds to the primary mouse button click (usually left)
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
           if self.isHidden() or self.isMinimized():
               self.show_window()
           else:
               # Optionally hide instead of doing nothing when visible
               # self.hide()
               pass # Currently does nothing if window is visible

    def show_window(self):
        """Shows and activates the main window."""
        self.showNormal() # Restores window if minimized or maximized
        self.activateWindow() # Brings the window to the front

    # --- Window Closing / Application Quitting ---
    def closeEvent(self, event):
        """Overrides the default window close event (clicking the 'X').
           Hides the window to the system tray instead of quitting.
        """
        event.ignore() # Prevent the window from closing immediately
        self.hide() # Hide the main window
        # Show a balloon message from the tray icon
        self.tray_icon.showMessage(
            config.APP_NAME,
            "Application minimized to tray.",
            QSystemTrayIcon.Information, # Icon type for the message
            2000 # Duration in milliseconds
        )

    def quit_application(self):
        """Safely stops the worker thread and quits the entire application."""
        self.append_log("Quit action triggered. Stopping worker thread...")
        # Ensure tray icon is hidden before potential blocking waits
        self.tray_icon.hide()

        if self.thread.isRunning():
            self.worker.stop() # Tell the worker loop to exit
            self.thread.quit() # Ask the QThread event loop to exit
            # Wait for the thread to finish gracefully (max 5 seconds)
            if not self.thread.wait(5000):
                self.append_log("[Warning] Worker thread did not stop gracefully. Terminating.")
                self.thread.terminate() # Force termination if it hangs
                self.thread.wait() # Wait after termination
            else:
                self.append_log("Worker thread stopped.")
        else:
             self.append_log("Worker thread was not running.")

        self.append_log("Quitting application.")
        QApplication.instance().quit() # Quit the Qt application event loop 
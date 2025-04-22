#!/usr/bin/env python3
# main.py
# Main entry point for the Dragon-Wilds Auto-Sync application.

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, 
                            QMenu, QAction, QTextEdit, QVBoxLayout, 
                            QWidget, QMessageBox, QLabel, QPushButton)
from PyQt5.QtCore import QThread, Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap

import config
from worker import Worker
from main_window import MainWindow

def run_application():
    """Initializes and runs the PyQt5 application."""

    # --- Configuration Check ---
    # Check if configuration seems to be default before starting
    error_message = config.get_config_error_message()
    if error_message:
        app_check = QApplication(sys.argv) # Need an app instance for MessageBox
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Configuration Warning")
        msg_box.setText(error_message)
        msg_box.setInformativeText("You can configure these settings in the application.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        print(f"Configuration Warning: {error_message}") # Also print to console
        # Continue execution with defaults instead of exiting

    # --- Initialize Application ---
    app = QApplication(sys.argv)

    # Keep the application running even when the main window is hidden (important for tray apps)
    app.setQuitOnLastWindowClosed(False)

    # --- Create and Show Main Window ---
    main_window = MainWindow()
    main_window.show() # Show the main window on startup

    # --- Start Event Loop ---
    # Start the Qt event loop. Execution hangs here until the application quits.
    sys.exit(app.exec_())


# --- Main Execution Guard ---
if __name__ == "__main__":
    run_application() 
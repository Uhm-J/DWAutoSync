# settings_dialog.py
# Defines the SettingsDialog class for configuring application settings

import json
import os
from pathlib import Path

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt

class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 200)
        
        # Initialize settings
        self.config_path = self.get_config_path()
        self.settings = self.load_settings()
        
        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface components."""
        main_layout = QVBoxLayout(self)
        
        # Form for settings
        form_layout = QFormLayout()
        
        # User name field
        self.name_edit = QLineEdit(self.settings.get("user_name", ""))
        form_layout.addRow("User Name:", self.name_edit)
        
        # API key field
        self.api_key_edit = QLineEdit(self.settings.get("api_key", ""))
        form_layout.addRow("API Key:", self.api_key_edit)
        
        # Server URL field
        self.server_url_edit = QLineEdit(self.settings.get("server_url", ""))
        self.server_url_edit.setPlaceholderText("e.g., https://dragonwilds.com/api")
        form_layout.addRow("Server URL:", self.server_url_edit)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.save_and_close)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
    def get_config_path(self):
        """Get the path to the config file."""
        # Store in user's documents folder
        if os.name == 'nt':  # Windows
            config_dir = os.path.join(os.path.expanduser("~"), "Documents", "DragonWildsAutoSync")
        else:  # Linux/Mac
            config_dir = os.path.join(os.path.expanduser("~"), ".config", "DragonWildsAutoSync")
            
        # Create directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, "settings.json")
        
    def load_settings(self):
        """Load settings from JSON file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                
        # Default settings
        return {
            "user_name": "",
            "api_key": "",
            "server_url": "https://dragonwilds.com/api"
        }
        
    def save_settings(self):
        """Save settings to JSON file."""
        settings = {
            "user_name": self.name_edit.text().strip(),
            "api_key": self.api_key_edit.text().strip(),
            "server_url": self.server_url_edit.text().strip()
        }
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=4)
            self.settings = settings
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            return False
            
    def save_and_close(self):
        """Save settings and close dialog if successful."""
        if self.validate_settings():
            if self.save_settings():
                self.accept()
                
    def validate_settings(self):
        """Validate settings before saving."""
        if not self.server_url_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Server URL cannot be empty")
            return False
            
        if not self.api_key_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "API Key cannot be empty")
            return False
            
        return True
        
    def get_current_settings(self):
        """Return the current settings."""
        return self.settings 
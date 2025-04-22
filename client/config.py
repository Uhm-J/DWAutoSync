# config.py
# Stores configuration constants for the Dragon-Wilds Auto-Sync Client

import json
import os
import pathlib

# --- Core Settings ---
TARGET_PROCESS_NAME = "RSDragonwilds-Win64-Shipping.exe"
POLLING_INTERVAL_SECONDS = 5

# --- Save File Location ---
# ** REPLACE: Folder name within the user's config/AppData directory **
# Example for Windows (%APPDATA%): "My Games\\DragonWilds"
# Example for Linux (~/.config): "DragonWilds"
SAVE_FOLDER_NAME = "\RSDragonwilds\Saved\SaveGames"
# ** REPLACE: The actual save file name **
SAVE_FILE_NAME = "DragonWilds.sav"  # Default save file name

# --- UI Settings ---
# ** REPLACE with the actual path to your icon file **
ICON_PATH = "icon.ico"
APP_NAME = "Dragon-Wilds Auto-Sync"

# --- Default Server and Authentication ---
DEFAULT_SERVER_URL = "https://dragonwilds.com/api"
DEFAULT_API_KEY = "TEST_API_KEY"
AUTH_HEADER_KEY = "X-API-Key"

# Path to the config file
def get_config_path():
    """Get the path to the config file."""
    # Store in user's documents folder
    if os.name == 'nt':  # Windows
        config_dir = os.path.join(os.path.expanduser("~"), "Documents", "DragonWildsAutoSync")
    else:  # Linux/Mac
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "DragonWildsAutoSync")
        
    # Create directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    return os.path.join(config_dir, "settings.json")

# Dynamic settings that can be loaded from JSON
def load_settings():
    """Load settings from JSON file if available, otherwise use defaults."""
    config_path = get_config_path()
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                settings = json.load(f)
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    # Return default settings if file doesn't exist or there's an error
    return {
        "user_name": "",
        "api_key": DEFAULT_API_KEY,
        "server_url": DEFAULT_SERVER_URL,
        "save_file_name": SAVE_FILE_NAME
    }

# Load settings from file
SETTINGS = load_settings()

# --- Server and Authentication ---
# Use settings from JSON if available, otherwise use defaults
SERVER_URL = SETTINGS.get("server_url", DEFAULT_SERVER_URL)
API_KEY = SETTINGS.get("api_key", DEFAULT_API_KEY)
USER_NAME = SETTINGS.get("user_name", "")
SAVE_FILE_NAME = SETTINGS.get("save_file_name", SAVE_FILE_NAME)

if not SAVE_FILE_NAME.endswith(".sav"):
    SAVE_FILE_NAME = SAVE_FILE_NAME + ".sav"

# Construct the full upload URL by appending /upload if needed
SERVER_UPLOAD_URL = SERVER_URL
if not SERVER_URL.endswith("/api/upload"):
    SERVER_UPLOAD_URL = f"{SERVER_URL}/api/upload"

# --- Helper function to check if config is valid ---
def is_config_default():
    """Checks if any configuration values are still set to their default placeholders."""
    return (
        not API_KEY or API_KEY == DEFAULT_API_KEY or
        not SERVER_URL or 
        not pathlib.Path(ICON_PATH).is_file() # Also check if icon exists
    )

def get_config_error_message():
    """Gets a message detailing which configuration values might be missing."""
    errors = []
    if not API_KEY or API_KEY == DEFAULT_API_KEY:
        errors.append("API Key is not set.")
    if not SERVER_URL:
        errors.append("Server URL is not set.")
    if not pathlib.Path(ICON_PATH).is_file():
        errors.append(f"Icon file not found at: {ICON_PATH}")
    if not SAVE_FOLDER_NAME or SAVE_FOLDER_NAME == "DragonWildsSaveFolderName":
        errors.append("Save Folder Name is not set.")
    if not SAVE_FILE_NAME or SAVE_FILE_NAME == "YourSaveFileName.sav":
        errors.append("Save File Name is not set.")
    
    if errors:
        return "Please configure the following:\n- " + "\n- ".join(errors)
    return "" 
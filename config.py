# config.py
# Stores configuration constants for the Dragon-Wilds Auto-Sync Client

import pathlib

# --- Core Settings ---
TARGET_PROCESS_NAME = "DragonWilds.exe"
POLLING_INTERVAL_SECONDS = 5

# --- Server and Authentication ---
# ** REPLACE with your actual server upload URL **
SERVER_UPLOAD_URL = "YOUR_SERVER_UPLOAD_URL"
# ** REPLACE with your actual API Key/Token **
API_KEY = "YOUR_API_KEY"
# Header name for the API key (adjust if needed by your server)
AUTH_HEADER_KEY = "X-API-Key"

# --- Save File Location ---
# ** REPLACE: Folder name within the user's config/AppData directory **
# Example for Windows (%APPDATA%): "My Games\\DragonWilds"
# Example for Linux (~/.config): "DragonWilds"
SAVE_FOLDER_NAME = "DragonWildsSaveFolderName"
# ** REPLACE: The actual save file name **
SAVE_FILE_NAME = "YourSaveFileName.sav"

# --- UI Settings ---
# ** REPLACE with the actual path to your icon file **
ICON_PATH = "icon.png"
APP_NAME = "Dragon-Wilds Auto-Sync"

# --- Helper function to check if config is default ---
def is_config_default():
    """Checks if any configuration values are still set to their default placeholders."""
    return (
        "YOUR_SERVER_UPLOAD_URL" in SERVER_UPLOAD_URL or
        "YOUR_API_KEY" in API_KEY or
        "DragonWildsSaveFolderName" == SAVE_FOLDER_NAME or
        "YourSaveFileName.sav" == SAVE_FILE_NAME or
        not pathlib.Path(ICON_PATH).is_file() # Also check if icon exists
    )

def get_config_error_message():
    """Gets a message detailing which configuration values might be missing."""
    errors = []
    if "YOUR_SERVER_UPLOAD_URL" in SERVER_UPLOAD_URL:
        errors.append("Server Upload URL is not set.")
    if "YOUR_API_KEY" in API_KEY:
        errors.append("API Key is not set.")
    if "DragonWildsSaveFolderName" == SAVE_FOLDER_NAME:
        errors.append("Save Folder Name is not set.")
    if "YourSaveFileName.sav" == SAVE_FILE_NAME:
        errors.append("Save File Name is not set.")
    if not pathlib.Path(ICON_PATH).is_file():
        errors.append(f"Icon file not found at: {ICON_PATH}")
    return "Please configure the following in config.py:\n- " + "\n- ".join(errors) 
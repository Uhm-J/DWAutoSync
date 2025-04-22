"""
Utility functions for the Dragon Wilds Auto-Sync server.
"""
import os
import json
from pathlib import Path

def read_api_keys():
    """
    Read API keys from the keys.json file.
    If the file doesn't exist, create it with a default test key.
    
    Returns:
        dict: A dictionary mapping user IDs to API keys
    """
    keys_file = Path("keys.json")
    
    # Create default keys file if it doesn't exist
    if not keys_file.exists():
        default_keys = {
            "test_user": "TEST_API_KEY"
        }
        
        with open(keys_file, "w") as f:
            json.dump(default_keys, f, indent=4)
        
        return default_keys
    
    # Read existing keys file
    try:
        with open(keys_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading API keys: {e}")
        return {"test_user": "TEST_API_KEY"}

def get_user_by_api_key(api_key):
    """
    Get user ID for the given API key.
    
    Args:
        api_key (str): The API key to look up
        
    Returns:
        str or None: The user ID if found, None otherwise
    """
    api_keys = read_api_keys()
    print(f"API keys: {api_keys}")
    print(f"API key: {api_key}")
    for user_id, key in api_keys.items():
        if key == api_key:
            return user_id
    
    return None

def get_user_save_info(user_id):
    """
    Get information about the user's save files.
    
    Args:
        user_id (str): The user ID to get information for
        
    Returns:
        dict: A dictionary containing save file information
    """
    upload_dir = Path("uploads") / user_id
    
    # Check if user directory exists
    if not upload_dir.exists() or not upload_dir.is_dir():
        return {
            "has_save": False,
            "saves_count": 0,
            "last_upload_time": None,
            "latest_save_path": None
        }
    
    # Count save files (excluding latest_* files)
    saves_count = 0
    latest_save_path = None
    last_upload_time = None
    
    # Find the latest save file (which starts with latest_)
    for file_path in upload_dir.glob("latest_*"):
        if file_path.is_file():
            latest_save_path = file_path
            break
    
    # Count all save files except the latest_* files
    for file_path in upload_dir.glob("*"):
        if file_path.is_file() and not file_path.name.startswith("latest_"):
            saves_count += 1
            
            # Try to determine the last upload time from the filename format: user_id_YYYYMMDD-HHMMSS_filename
            try:
                timestamp_part = file_path.name.split("_")[1]
                if not last_upload_time or timestamp_part > last_upload_time:
                    last_upload_time = timestamp_part
            except:
                pass
    
    # Format the timestamp for display (YYYYMMDD-HHMMSS to YYYY-MM-DD HH:MM:SS)
    if last_upload_time:
        try:
            date_part = last_upload_time.split("-")[0]
            time_part = last_upload_time.split("-")[1]
            formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]}"
            formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
            last_upload_time = f"{formatted_date} {formatted_time}"
        except:
            pass
    
    return {
        "has_save": latest_save_path is not None,
        "saves_count": saves_count,
        "last_upload_time": last_upload_time,
        "latest_save_path": latest_save_path
    }

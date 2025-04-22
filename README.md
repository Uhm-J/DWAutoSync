# Dragon-Wilds Auto-Sync

A utility application that monitors for the Dragon Wilds game process and automatically syncs save files to a server when the game closes.

## Features

- System tray application that runs in the background
- Monitors for the Dragon Wilds game process
- Automatically uploads save files when the game closes
- Manual upload option
- Configurable settings

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure the application by editing `config.py`:
   - Set your server upload URL
   - Add your API key
   - Configure the save folder name and file name
   - Add an icon file (optional)

3. Run the application:
   ```
   python main.py
   ```

## Configuration

Before running the application, you need to edit the `config.py` file to specify:

- `SERVER_UPLOAD_URL`: The URL endpoint where save files will be uploaded
- `API_KEY`: Your authentication key for the server
- `SAVE_FOLDER_NAME`: The folder name within the AppData/config directory
- `SAVE_FILE_NAME`: The name of the save file to upload
- `ICON_PATH`: Path to an icon file (optional)

## How It Works

The application creates a worker thread that periodically checks if the Dragon Wilds game process is running. When it detects that the game has closed, it automatically uploads the save file to the configured server.

The main application runs in the system tray, allowing it to operate in the background without cluttering your desktop.

## System Requirements

- Python 3.6 or higher
- PyQt5
- Windows, macOS, or Linux operating system 
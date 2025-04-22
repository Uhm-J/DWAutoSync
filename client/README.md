# Dragon Wilds Auto-Sync Client

A desktop application that automatically synchronizes your Dragon Wilds save files with a server. When the game closes, your save file is automatically uploaded to the server, ensuring you always have a backup.

## Features

- System tray application that runs in the background
- Monitors for the Dragon Wilds game process
- Automatically uploads save files when the game closes
- Options to manually upload or download save files
- Simple, configurable settings

## Installation

### Prerequisites
- Python 3.6 or higher
- PyQt5
- Requests library
- psutil library

### Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python main.py
   ```

3. For easy access, you can create a shortcut to the provided `run_app.bat` file.

## Configuration

The first time you run the application, you'll need to configure it through the Settings dialog.

1. Click the "Settings" button in the main window
2. Enter your information:
   - **User Name**: Your username for identification on the server
   - **API Key**: The authentication key provided by your server administrator
   - **Server URL**: The URL of the Dragon Wilds sync server (e.g., https://dragonwilds.com/api)
   - **Save File Name**: The name of your Dragon Wilds save file (usually "DragonWilds.sav")

The application stores its configuration in a JSON file located at:
- Windows: `%USERPROFILE%\Documents\DragonWildsAutoSync\settings.json`
- Linux/Mac: `~/.config/DragonWildsAutoSync/settings.json`

## Usage

### Main Window

- **Settings**: Open the settings dialog to configure the application
- **Ping Server**: Test the connection to the server
- **Force Upload Save**: Manually upload your current save file
- **Download Latest Save**: Download the latest save file from the server

### System Tray

The application runs in your system tray for convenient access:
- **Left-click**: Show/hide the main window
- **Right-click**: Opens a menu with options to show the window or quit the application

### Background Operation

Once configured, the application will:
1. Monitor for the Dragon Wilds game process
2. Detect when the game closes
3. Automatically upload your save file to the server
4. Display status messages in the log window

## Running at Startup

### Windows

1. Create a shortcut to `run_app.bat`
2. Press `Win+R` and type `shell:startup`
3. Copy the shortcut to the startup folder

### Linux

1. Create a .desktop file in `~/.config/autostart/`
2. Point it to the `main.py` script

### macOS

1. Go to System Preferences > Users & Groups
2. Select your user and click on Login Items
3. Click the + button and select the application

## Troubleshooting

- **Cannot connect to server**: Verify your server URL and API key in settings
- **Save file not found**: Check that the save file name and location are correct
- **Application not starting**: Ensure you have all required dependencies installed
- **Game not detected**: Make sure the game executable name is correct

## Additional Information

For more details on how the server works and API documentation, refer to the server's README file. 
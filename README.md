# Dragon Wilds Auto-Sync

An automatic save synchronization system for Dragon Wilds game, consisting of a client application that monitors when the game closes and automatically uploads save files to a server.

## Features

- System tray application that runs in the background
- Monitors when Dragon Wilds game is running
- Automatically uploads save files when the game closes
- Options to manually upload or download save files
- Server component to store and manage save files

## Project Structure

The project is organized into two main components:

### Client

The client is a desktop application that runs in the system tray and monitors when the Dragon Wilds game is closed. When the game closes, it automatically uploads the save file to the configured server.

The client is built with Python and PyQt5.

### Server

The server is a simple Flask application that receives save files from clients and stores them with timestamps and user identification.

The server provides RESTful API endpoints for:
- Uploading save files
- Checking server status
- Viewing API documentation

## Development Setup

### Client Development

1. Clone the repository
2. Navigate to the `client` directory
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```
4. Run the client:
   ```
   python main.py
   ```

### Server Development

1. Navigate to the `server` directory
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the server:
   ```
   python server.py
   ```

## Building the Application

### Prerequisites

- Python 3.6 or higher
- PyInstaller (installed automatically by the build script)
- 7-Zip (optional, for automatic packaging)

### Build Process

The project includes a build script that automates the build process:

1. Navigate to the project root directory
2. Run the build script:
   ```
   build_release.bat
   ```

The build script performs the following steps:
1. Extracts the version number from `client/version.py`
2. Removes any existing executable
3. Builds the application using PyInstaller
4. Creates the distribution directory structure
5. Updates the README with the current version
6. Creates a ZIP file of the distribution

### Manual Build

If you prefer to build manually:

1. Navigate to the client directory:
   ```
   cd client
   ```

2. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

3. Build the executable:
   ```
   pyinstaller --onefile --windowed --icon=icon.ico --name=DWAutoSync --add-data="icon.ico;." --add-data="icon.png;." main.py
   ```

4. The executable will be created in the `dist` directory

## Deployment

### Client Distribution

After building, you can distribute the application by providing the following:
- DWAutoSync.exe
- README.txt (with configuration instructions)

Users only need to run the executable and configure their settings.

### Server Deployment

For production deployment, it's recommended to:

1. Deploy the server to a dedicated host or cloud platform
2. Set up proper authentication and HTTPS
3. Configure clients with the production server URL

## Documentation

- Client user documentation is in the build directory's README.txt
- Server API documentation is provided via an endpoint in the server application

## Version History

See the releases page for version history information. 
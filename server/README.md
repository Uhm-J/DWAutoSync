# Dragon Wilds Auto-Sync Server

A simple Flask server to receive and store Dragon Wilds save files from clients.

## Features

- Receives save files from Dragon Wilds Auto-Sync clients
- Stores files with timestamps and user identification
- Keeps track of the latest save for each user
- Logs all uploads for record-keeping
- Simple API key authentication
- Web interface for users to download their save files

## Setup

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Configure API keys in `keys.json`:
   ```json
   {
       "user1": "YOUR_API_KEY_1",
       "user2": "YOUR_API_KEY_2"
   }
   ```
   (A default `keys.json` will be created if it doesn't exist)

3. Set a secret key for session encryption (in production):
   ```
   export SECRET_KEY="your-secret-key"
   ```

4. Run the server:
   ```
   python server.py
   ```

The server will be available at http://localhost:5000.

## Web Interface

The server provides a simple web interface for users to:

1. Log in using their API key
2. View their account information
3. Download their latest save file

### Accessing the Web Interface

Simply navigate to the server URL (e.g., http://localhost:5000) in a web browser.

## API Endpoints

- **GET /** - Web interface (login page or dashboard)
- **GET /api** - API documentation
- **GET /api/status** - Server status information
- **POST /api/upload** - Upload a save file

### Authentication

API requests should include an API key in the header:

```
X-API-Key: YOUR_API_KEY
```

### Upload Example

```
POST /api/upload
Headers:
  X-API-Key: YOUR_API_KEY
  X-User-Name: PlayerName
Files:
  savefile: [binary file content]
```

## Directory Structure

- `uploads/` - All uploaded save files organized by user ID
- `logs/` - Server logs including upload records
- `templates/` - HTML templates for the web interface

## Deployment

For production deployment, it's recommended to:

1. Use a production WSGI server like gunicorn:
   ```
   gunicorn -w 4 -b 0.0.0.0:5000 server:app
   ```

2. Set up a reverse proxy with nginx or Apache

3. Use a proper session secret key (environment variable)

4. Implement HTTPS for secure API key transmission 
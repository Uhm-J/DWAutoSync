#!/usr/bin/env python3
# server.py
# Simple Flask server for Dragon-Wilds save file storage

import os
import time
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
from utils import read_api_keys, get_user_by_api_key, get_user_save_info

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Create directories for save files and logs
UPLOAD_FOLDER = Path("uploads")
LOG_FOLDER = Path("logs") 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# Configuration
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload size


# Load API keys
API_KEYS = read_api_keys()

# --- Web UI Routes ---

@app.route("/")
def index():
    """Main web page"""
    # If user is logged in, redirect to dashboard
    if "api_key" in session:
        return redirect(url_for("dashboard"))
    
    # Otherwise show the login page
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle login form submission"""
    if request.method == "POST":
        api_key = request.form.get("api_key")
        
        # Validate API key
        user_id = get_user_by_api_key(api_key)
        
        if user_id:
            # Store API key in session
            session["api_key"] = api_key
            session["user_id"] = user_id
            
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid API key")
    
    # GET request - show login form
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    """User dashboard page"""
    # Check if user is logged in
    if "api_key" not in session:
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    api_key = session["api_key"]
    
    # Get user's save information
    save_info = get_user_save_info(user_id)
    
    # Get user's name from headers or use user_id as fallback
    user_name = user_id
    
    return render_template(
        "dashboard.html", 
        user_id=user_id,
        user_name=user_name,
        has_save=save_info["has_save"],
        saves_count=save_info["saves_count"],
        last_upload_time=save_info["last_upload_time"],
        save_files=save_info["save_files"]
    )

@app.route("/download-latest-web")
def download_latest_save_web():
    """Download the user's latest save file"""
    # Check if user is logged in
    if "api_key" not in session:
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    
    # Get save file name from the query parameter
    save_file = request.args.get("save_file")
    
    # If no save file specified, show the save file selection page
    if not save_file:
        # Get user's save information
        save_info = get_user_save_info(user_id)
        
        if not save_info["has_save"]:
            return "No save files found", 404
        
        # If there's only one save file, download it directly
        if len(save_info["save_files"]) == 1:
            save_path = save_info["save_files"][0]["path"]
            world_name = save_info["save_files"][0]["world_name"]
            return send_file(
                save_path,
                as_attachment=True,
                download_name=world_name
            )
        
        # Otherwise, show the template with all save files
        return render_template(
            "save_files.html",
            user_id=user_id,
            user_name=session.get("user_name", user_id),
            save_files=save_info["save_files"]
        )
    
    # Otherwise, download the specified save file
    upload_dir = Path("uploads")
    save_path = upload_dir / f"latest_{save_file}"
    
    if not save_path.exists():
        return "Save file not found", 404
    
    return send_file(
        save_path,
        as_attachment=True,
        download_name=save_file
    )

@app.route("/logout")
def logout():
    """Log the user out"""
    session.pop("api_key", None)
    session.pop("user_id", None)
    return redirect(url_for("login"))

# --- API Routes ---

@app.route("/api")
def api_docs():
    """API documentation"""
    return jsonify({
        "endpoints": [
            {"path": "/api/upload", "method": "POST", "description": "Upload a save file"},
            {"path": "/api/status", "method": "GET", "description": "Check server status"}
        ]
    })

@app.route("/api/status", methods=["GET"])
def api_status():
    """API status endpoint"""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({"error": "Missing API key"}), 401
    
    user_id = get_user_by_api_key(api_key)
    if not user_id:
        return jsonify({"error": "Invalid API key"}), 401
    
    # Get user information
    user_name = request.headers.get("X-User-Name", "unknown_user")
    
    # Get user's save information
    user_saves = get_user_save_info(user_id)

    return jsonify({
        "status": "online",
        "time": datetime.now().isoformat(),
        "saves_count": user_saves["saves_count"],
        "user_id": user_id,
        "user_name": user_name
    })

@app.route("/api/upload", methods=["POST"])
def upload_save():
    """Endpoint to receive and store a save file upload"""
    # Check for API key authentication
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({"error": "Missing API key"}), 401
    
    user_id = get_user_by_api_key(api_key)
    if not user_id:
        return jsonify({"error": "Invalid API key"}), 401
    
    # Get user information
    user_name = request.headers.get("X-User-Name", "unknown_user")
    
    # Check if the POST request has the file part
    if "savefile" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    print(f"Received file: {request.files['savefile']}")
    
    file = request.files["savefile"]
    
    # If the user does not select a file, the browser might
    # submit an empty file without a filename
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    # Save the file with a timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    orig_filename = secure_filename(file.filename)
    filename = f"{user_id}_{timestamp}_{orig_filename}"
    
    # Create user folder if it doesn't exist
    user_folder = UPLOAD_FOLDER
    os.makedirs(user_folder, exist_ok=True)
    
    # Save the file and log the upload
    file_path = user_folder / filename
    print(f"Saving file to: {file_path}")
    file.save(file_path)
    
    # Copy as latest.sav for easy access to most recent save
    latest_path = user_folder / f"latest_{orig_filename}"
    print(f"Copying to latest: {latest_path}")
    with open(file_path, "rb") as src:
        with open(latest_path, "wb") as dst:
            dst.write(src.read())
    
    # Log the upload
    log_upload(user_id, user_name, filename, request.remote_addr)
    
    return jsonify({
        "success": True,
        "message": "File saved successfully",
        "filename": filename,
        "timestamp": timestamp
    })

@app.route("/download-client")
def download_client():
    """Download the client"""
    return send_file("DWAutoSync.zip", as_attachment=True)

@app.route("/api/download-latest")
def download_latest_save():
    """Download the user's latest save file"""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({"error": "Missing API key"}), 401
    
    user_id = get_user_by_api_key(api_key)
    if not user_id:
        return jsonify({"error": "Invalid API key"}), 401
    
    # Get user information
    user_name = request.headers.get("X-User-Name", "unknown_user")

    # Find the latest save file
    save_file_name = request.headers.get("save_file_name", "DragonWilds.sav")

    file_name = UPLOAD_FOLDER / f"latest_{save_file_name}"
    print(f"Downloading latest save file: {file_name}")

    if not file_name.exists():
        return jsonify({"error": "No save file found"}), 404
    
    # Return the file as a download
    return send_file(
        file_name,
        as_attachment=True,
        download_name=save_file_name
    )

def log_upload(user_id, user_name, filename, ip_address):
    """Log the upload to the log file"""
    log_file = LOG_FOLDER / "uploads.log"
    with open(log_file, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {user_id} - {user_name} - {filename} - {ip_address}\n")

def count_saves():
    """Count total number of save files stored"""
    count = 0
    for path in UPLOAD_FOLDER.glob("**/*"):
        if path.is_file() and not path.name.startswith("latest_"):
            count += 1
    return count

if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=6900, debug=True) 
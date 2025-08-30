#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoH2 Application Startup Script
Starts both the backend server and opens the frontend in a web browser
"""

import os
import sys
import time
import webbrowser
import subprocess
import threading
from pathlib import Path

def print_banner():
    """Print the GeoH2 startup banner"""
    print("=" * 60)
    print("🌍 GeoH2 - Hydrogen Cost Analysis Platform")
    print("=" * 60)
    print("🚀 Starting backend server and frontend...")
    print("=" * 60)

def check_backend_dependencies():
    """Check if backend dependencies are available"""
    print("📋 Checking backend dependencies...")
    
    backend_dir = Path(__file__).parent / "backend"
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    required_files = [
        "main.py",
        "api_server.py",
        "config.py"
    ]
    
    for file in required_files:
        if not (backend_dir / file).exists():
            print(f"❌ Required file not found: {file}")
            return False
    
    print("✅ Backend dependencies check passed")
    return True

def check_frontend_files():
    """Check if frontend files are available"""
    print("📋 Checking frontend files...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    required_files = [
        "index.html",
        "styles.css",
        "app.js"
    ]
    
    for file in required_files:
        if not (frontend_dir / file).exists():
            print(f"❌ Required file not found: {file}")
            return False
    
    print("✅ Frontend files check passed")
    return True

def start_backend_server():
    """Start the backend server in a separate thread"""
    print("🔧 Starting backend server...")
    
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    try:
        # Start the API server
        subprocess.run([sys.executable, "api_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend server failed to start: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")

def wait_for_backend():
    """Wait for the backend server to be ready"""
    print("⏳ Waiting for backend server to start...")
    
    import requests
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend server is ready!")
                return True
        except:
            pass
        
        attempt += 1
        time.sleep(1)
        if attempt % 5 == 0:
            print(f"   Still waiting... ({attempt}/{max_attempts})")
    
    print("❌ Backend server failed to start within timeout")
    return False

def open_frontend():
    """Open the frontend in the default web browser"""
    print("🌐 Opening frontend in web browser...")
    
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    frontend_url = f"file:///{frontend_path.absolute().as_posix()}"
    
    try:
        webbrowser.open(frontend_url)
        print("✅ Frontend opened in web browser")
        print(f"📍 Frontend URL: {frontend_url}")
        print("🔗 Backend API: http://localhost:8000")
    except Exception as e:
        print(f"❌ Failed to open frontend: {e}")
        print(f"📍 Please manually open: {frontend_url}")

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_backend_dependencies():
        print("\n❌ Backend dependency check failed. Please ensure all files are present.")
        return
    
    if not check_frontend_files():
        print("\n❌ Frontend file check failed. Please ensure all files are present.")
        return
    
    print("\n✅ All checks passed!")
    
    # Start backend server in background thread
    backend_thread = threading.Thread(target=start_backend_server, daemon=True)
    backend_thread.start()
    
    # Wait for backend to be ready
    if wait_for_backend():
        # Open frontend
        open_frontend()
        
        print("\n🎉 GeoH2 application started successfully!")
        print("\n📱 Frontend: Open in your web browser")
        print("🔧 Backend: Running on http://localhost:8000")
        print("📊 API Documentation: http://localhost:8000")
        
        print("\n💡 Tips:")
        print("   - Keep this terminal open to run the backend")
        print("   - Use Ctrl+C to stop the backend server")
        print("   - Refresh the frontend page if needed")
        print("   - Check the backend terminal for any error messages")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down GeoH2 application...")
            print("✅ Application stopped successfully")
    
    else:
        print("\n❌ Failed to start GeoH2 application")
        print("💡 Troubleshooting:")
        print("   - Check if port 8000 is available")
        print("   - Ensure no other services are using port 8000")
        print("   - Check backend logs for error messages")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Application startup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check the error message and try again") 
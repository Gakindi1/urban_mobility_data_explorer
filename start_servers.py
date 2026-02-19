#!/usr/bin/env python3
"""
Start both the backend Flask server and frontend HTTP server
"""
import subprocess
import time
import sys
import os

def main():
    print("=" * 70)
    print("NYC TAXI URBAN MOBILITY EXPLORER - Starting Servers")
    print("=" * 70)
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    print(f"\nStarting Flask Backend on port 5000...")
    print(f"Backend directory: {backend_dir}")
    backend_process = subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print(f"Starting Frontend Server on port 8000...")
    print(f"Frontend directory: {frontend_dir}")
    frontend_process = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '8000'],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("\n" + "=" * 70)
    print("Servers started!")
    print("=" * 70)
    print(f"\nFrontend (HTML/CSS/JS): http://127.0.0.1:8000")
    print(f"Backend API: http://127.0.0.1:5000/api")
    print(f"\nOpen your browser to: http://127.0.0.1:8000")
    print("\nPress Ctrl+C to stop all servers...")
    print("=" * 70 + "\n")
    
    try:
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait(timeout=5)
        frontend_process.wait(timeout=5)
        print("Servers stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()

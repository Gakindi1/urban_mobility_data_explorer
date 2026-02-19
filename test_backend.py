import urllib.request
import json
import time

try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/health', timeout=3)
    data = json.loads(response.read())
    print(f"✓ Backend is running and responding!")
    print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"✗ Backend is not responding: {type(e).__name__}: {e}")
    print("Note: The backend may still be initializing. Please wait a moment and try again.")

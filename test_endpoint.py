import sys
sys.path.insert(0, '.')
from app import app
import traceback

# Test the payment-types endpoint
with app.test_client() as client:
    try:
        response = client.get('/api/trips/payment-types')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

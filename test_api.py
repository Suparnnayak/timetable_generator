"""
Test script for Flask API
Run this after starting the Flask server to test the endpoints
"""
import requests
import json
import os

BASE_URL = "http://localhost:5000"

# Load sample data
BASE = os.path.join(os.path.dirname(__file__), 'timetable_ai', 'dummy_data')

def load_sample_data():
    """Load sample data from JSON files"""
    return {
        "time_slots": json.load(open(os.path.join(BASE, 'slots.json'))),
        "courses": json.load(open(os.path.join(BASE, 'courses.json'))),
        "faculty": json.load(open(os.path.join(BASE, 'faculty.json'))),
        "rooms": json.load(open(os.path.join(BASE, 'rooms.json'))),
        "student_groups": json.load(open(os.path.join(BASE, 'groups.json'))),
        "time_limit": 10
    }

def test_health_check():
    """Test health check endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_api_info():
    """Test API info endpoint"""
    print("Testing /api/info endpoint...")
    response = requests.get(f"{BASE_URL}/api/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_validate():
    """Test validate endpoint"""
    print("Testing /api/validate endpoint...")
    data = load_sample_data()
    response = requests.post(
        f"{BASE_URL}/api/validate",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_generate():
    """Test generate endpoint"""
    print("Testing /api/generate endpoint...")
    data = load_sample_data()
    
    print("Sending request...")
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if result.get('success'):
        print("✅ Timetable generated successfully!")
        print(f"Time slots used: {result['metadata']['time_slots_used']}")
        print(f"Students scheduled: {result['metadata']['students_scheduled']}")
        print(f"Violations: {result['metadata']['violations_count']}")
        
        # Save output to file
        output_file = "api_output.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nFull output saved to: {output_file}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        print(f"Message: {result.get('message', '')}")
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("NEP Timetable Generator API - Test Script")
    print("=" * 60)
    print()
    
    try:
        # Test health check
        test_health_check()
        
        # Test API info
        test_api_info()
        
        # Test validate
        test_validate()
        
        # Test generate
        test_generate()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the Flask server is running:")
        print("  python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")


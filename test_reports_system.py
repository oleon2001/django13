#!/usr/bin/env python3
"""
Test script for the reports system.
"""
import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/reports"

def test_available_reports():
    """Test the available reports endpoint."""
    print("Testing available reports endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/available/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Available reports:")
            for report in data.get('reports', []):
                print(f"  - {report['name']} ({report['type']})")
                print(f"    Formats: {', '.join(report['formats'])}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure Django is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_report_templates():
    """Test the report templates endpoint."""
    print("\nTesting report templates endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/templates/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('templates', []))} templates")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure Django is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_report_statistics():
    """Test the report statistics endpoint."""
    print("\nTesting report statistics endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/statistics/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print(f"Total executions: {stats.get('total_executions', 0)}")
            print(f"Completed executions: {stats.get('completed_executions', 0)}")
            print(f"Success rate: {stats.get('success_rate', 0):.1f}%")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure Django is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_generate_report():
    """Test report generation (this will likely fail without authentication)."""
    print("\nTesting report generation endpoint...")
    
    # Get a sample device ID (you'll need to adjust this)
    device_id = 1  # Assuming device ID 1 exists
    
    # Date range for the last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    payload = {
        'report_type': 'stats',
        'device_id': device_id,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'format': 'pdf'
    }
    
    try:
        response = requests.post(f"{API_BASE}/generate/", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Report generated successfully!")
        elif response.status_code == 401:
            print("Authentication required (expected)")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure Django is running.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all tests."""
    print("=== Reports System Test ===")
    print(f"Testing endpoints at: {API_BASE}")
    print()
    
    test_available_reports()
    test_report_templates()
    test_report_statistics()
    test_generate_report()
    
    print("\n=== Test Complete ===")
    print("Note: Some endpoints may require authentication.")
    print("To test with authentication, you'll need to:")
    print("1. Create a user account")
    print("2. Get an authentication token")
    print("3. Include the token in the Authorization header")

if __name__ == "__main__":
    main() 
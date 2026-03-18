
import requests
import json

# Base URL of your Flask app
BASE_URL = "http://localhost:5000"

def test_home_page():
    """Test if the home page loads"""
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Home page loaded successfully!")
            return True
        else:
            print(f"❌ Home page failed with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running!")
        return False

def test_prediction_api():
    """Test the prediction API with sample data"""
    
    # Sample test data based on YOUR actual features
    test_cases = [
        {
            "name": "Successful Startup (Software, USA)",
            "data": {
                "category_list": 3988,  # Software
                "funding_total_usd": 5000000,  # $5M
                "country_code": 37242,  # USA
                "city": 3522,  # San Francisco
                "funding_rounds": 4,
                "startup_age": 5,
                "funding_duration": 3
            }
        },
        {
            "name": "Risky Startup (Unknown, Low Funding)",
            "data": {
                "category_list": 3090,  # Unknown
                "funding_total_usd": 50000,  # $50K
                "country_code": 6933,  # Unknown
                "city": 7995,  # Unknown
                "funding_rounds": 1,
                "startup_age": 1,
                "funding_duration": 0
            }
        },
        {
            "name": "Indian E-Commerce Startup",
            "data": {
                "category_list": 1328,  # E-Commerce
                "funding_total_usd": 2000000,  # $2M
                "country_code": 1586,  # India
                "city": 293,  # Mumbai
                "funding_rounds": 2,
                "startup_age": 3,
                "funding_duration": 1
            }
        },
        {
            "name": "UK Biotech Startup",
            "data": {
                "category_list": 3598,  # Biotechnology
                "funding_total_usd": 10000000,  # $10M
                "country_code": 3668,  # UK
                "city": 1915,  # London
                "funding_rounds": 3,
                "startup_age": 4,
                "funding_duration": 2
            }
        }
    ]
    
    print("\n" + "="*60)
    print("🔬 TESTING PREDICTION API")
    print("="*60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print("-" * 40)
        print("Input Data:")
        for key, value in test_case['data'].items():
            print(f"  {key}: {value}")
        
        try:
            # Send POST request to prediction endpoint
            response = requests.post(
                f"{BASE_URL}/predict",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("\n✅ Prediction Successful!")
                    print(f"  Result: {'SUCCESS' if result['prediction'] == 1 else 'RISK'}")
                    print(f"  Message: {result['message']}")
                    if 'confidence' in result:
                        print(f"  Confidence: {result['confidence']:.1f}%")
                else:
                    print(f"\n❌ API Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"\n❌ HTTP Error {response.status_code}")
                print(f"  Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("\n❌ Cannot connect to server! Make sure Flask app is running on port 5000")
            return
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
        
        print("-" * 40)

def test_invalid_data():
    """Test API with invalid data"""
    print("\n" + "="*60)
    print("⚠️  TESTING INVALID DATA HANDLING")
    print("="*60)
    
    # Test with missing fields
    invalid_data = {
        "category_list": 3988,
        "funding_total_usd": 5000000
        # Missing other fields
    }
    
    print("\n📊 Test: Missing Fields")
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('success'):
                print(f"✅ API correctly caught error: {result.get('error')}")
            else:
                print("❌ API should have failed but succeeded!")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🚀 STARTUP SUCCESS PREDICTOR API TESTER")
    print("="*60)
    print(f"Target URL: {BASE_URL}")
    print("="*60)
    
    # First test if server is running
    if not test_home_page():
        print("\n❌ Please start your Flask app first with: python app.py")
        return
    
    # Test prediction API
    test_prediction_api()
    
    # Test invalid data
    test_invalid_data()
    
    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    main()
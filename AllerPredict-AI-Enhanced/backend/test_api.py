"""
Test Script for AllerPredict AI
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_health():
    print_section("1. Testing Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_get_products():
    print_section("2. Testing Get All Products")
    response = requests.get(f"{BASE_URL}/products")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Total Products: {len(data['products'])}")
    print(f"\nFirst Product:")
    print(json.dumps(data['products'][0], indent=2))
    return response.status_code == 200

def test_search():
    print_section("3. Testing Product Search")
    query = "cookies"
    response = requests.get(f"{BASE_URL}/search/{query}?limit=3")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Query: {data['query']}")
    print(f"Results Found: {len(data['results'])}")
    for i, result in enumerate(data['results'], 1):
        print(f"\n{i}. {result['name']} (Score: {result['similarity_score']:.2f})")
    return response.status_code == 200

def test_quick_analysis():
    print_section("4. Testing Quick Analysis")
    payload = {
        "query": "Almond Milk",
        "user_allergies": ["tree nuts"],
        "detailed_analysis": False
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    elapsed = time.time() - start_time
    
    print(f"\nStatus: {response.status_code}")
    print(f"Time: {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nProduct: {data['product']['name']}")
        print(f"Allergens: {', '.join(data['product']['allergens'])}")
        print(f"\nAnalysis Preview:")
        print(data['analysis'][:200] + "...")
        print(f"\nAlternatives Found: {len(data['alternatives'])}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_find_alternatives():
    print_section("5. Testing Find Alternatives")
    payload = {
        "allergens": ["peanuts", "dairy"],
        "category": "Snacks"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/alternatives", json=payload)
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Avoiding: {', '.join(data['allergens_avoided'])}")
        print(f"\nSafe Alternatives:")
        for i, alt in enumerate(data['alternatives'], 1):
            print(f"{i}. {alt['name']} by {alt['brand']}")
            print(f"   Allergens: {', '.join(alt['allergens']) if alt['allergens'] else 'None'}")
            print(f"   Score: {alt['ethical_score']}/10\n")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def run_all_tests():
    print("\n" + "🧪 "*30)
    print(" "*25 + "AllerPredict AI - Test Suite")
    print("🧪 "*30)
    
    tests = [
        ("Health Check", test_health),
        ("Get Products", test_get_products),
        ("Search", test_search),
        ("Quick Analysis", test_quick_analysis),
        ("Find Alternatives", test_find_alternatives),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")

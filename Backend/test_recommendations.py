"""
Test script for product recommendations API
Run this after starting the Backend server with: uvicorn main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if the server is running"""
    print("\n🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_stats():
    """Test collection stats"""
    print("\n📊 Getting collection stats...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total products: {data['total_products']}")
        print(f"Vectors: {data['vectors']}")
    else:
        print(f"Error: {response.text}")

def test_text_search(query, category=None, limit=5):
    """Test text-based product search"""
    print(f"\n🔎 Searching for: '{query}'")
    if category:
        print(f"   Category: {category}")
    
    payload = {
        "query": query,
        "limit": limit
    }
    if category:
        payload["category"] = category
    
    response = requests.post(f"{BASE_URL}/recommend/text", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"\n✅ Found {len(results)} products:")
        for i, product in enumerate(results, 1):
            print(f"\n{i}. {product['name']}")
            print(f"   ID: {product['product_id']}")
            print(f"   Category: {product['category']}")
            print(f"   Price: ${product['price']}")
            print(f"   Similarity Score: {product['score']:.4f}")
    else:
        print(f"❌ Error: {response.text}")
    
    return response

def test_similar_products(product_id, limit=5):
    """Test finding similar products"""
    print(f"\n🔗 Finding products similar to: {product_id}")
    
    response = requests.post(f"{BASE_URL}/recommend/similar/{product_id}?limit={limit}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"\n✅ Found {len(results)} similar products:")
        for i, product in enumerate(results, 1):
            print(f"\n{i}. {product['name']}")
            print(f"   ID: {product['product_id']}")
            print(f"   Category: {product['category']}")
            print(f"   Price: ${product['price']}")
            print(f"   Similarity Score: {product['score']:.4f}")
    else:
        print(f"❌ Error: {response.text}")
    
    return response

def test_smart_search(query, category=None, limit=5):
    """Test smart budget-aware search with fallback"""
    print(f"\n🧠 Smart search: '{query}'")
    if category:
        print(f"   Category: {category}")
    
    payload = {
        "query": query,
        "limit": limit
    }
    if category:
        payload["category"] = category
    
    response = requests.post(f"{BASE_URL}/recommend/smart", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n💡 Strategy: {data['strategy']}")
        print(f"📝 Explanation: {data['explanation']}")
        if data.get('budget_limit'):
            print(f"💰 Budget Limit: ${data['budget_limit']}")
        
        results = data['products']
        print(f"\n✅ Found {len(results)} products:")
        for i, product in enumerate(results, 1):
            print(f"\n{i}. {product['name']}")
            print(f"   ID: {product['product_id']}")
            print(f"   Category: {product['category']}")
            print(f"   Price: ${product['price']}")
            print(f"   Similarity Score: {product['score']:.4f}")
    else:
        print(f"❌ Error: {response.text}")
    
    return response

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 FURNIVERSE RECOMMENDATION API TESTS")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server not running! Start it with: uvicorn main:app --reload")
        return
    
    # Test 2: Stats
    test_stats()
    
    # Test 3: Text searches
    print("\n" + "=" * 60)
    print("TEXT-BASED SEARCHES")
    print("=" * 60)
    
    test_text_search("modern comfortable sofa for living room")
    test_text_search("minimalist bed frame", category="Bed Frames")
    test_text_search("cozy chair for reading")
    test_text_search("elegant dining table")
    
    # Test 4: Similar products (graph-based)
    print("\n" + "=" * 60)
    print("SIMILAR PRODUCTS (Graph-based)")
    print("=" * 60)
    
    # Get a product ID from the first search to test similar products
    response = requests.post(f"{BASE_URL}/recommend/text", json={"query": "sofa", "limit": 1})
    if response.status_code == 200 and len(response.json()) > 0:
        product_id = str(response.json()[0]['product_id'])  # Ensure it's a string
        test_similar_products(product_id)
    
    # Test 5: Smart budget-aware search
    print("\n" + "=" * 60)
    print("SMART BUDGET-AWARE SEARCH")
    print("=" * 60)
    
    test_smart_search("Italian leather sofa under $400")
    test_smart_search("modern comfortable bed frame under $300")
    test_smart_search("elegant dining table under $500")
    test_smart_search("luxury velvet sofa under $2000")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure the Backend server is running:")
        print("   cd Backend")
        print("   venv\\Scripts\\activate  (Windows)")
        print("   uvicorn main:app --reload")

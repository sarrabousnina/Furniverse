"""
Quick test for smart budget-aware search
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_smart_search(query):
    print("=" * 70)
    print(f"🔍 QUERY: {query}")
    print("=" * 70)
    
    response = requests.post(
        f"{BASE_URL}/recommend/smart",
        json={"query": query, "limit": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n💡 Strategy: {data['strategy']}")
        print(f"\n📝 {data['explanation']}")
        
        if data.get('budget_limit'):
            print(f"\n💰 Budget Limit: ${data['budget_limit']}")
        
        print(f"\n✨ Found {len(data['products'])} products:\n")
        
        for i, product in enumerate(data['products'], 1):
            print(f"{i}. {product['name']}")
            print(f"   💵 Price: ${product['price']}")
            print(f"   📊 Match Score: {product['score']:.4f}")
            print(f"   🏷️  Category: {product['category']}")
            
            if product.get('tags'):
                print(f"   🔖 Tags: {', '.join(product['tags'][:4])}")
            
            if product.get('colors'):
                print(f"   🎨 Colors: {', '.join(product['colors'][:3])}")
            
            print()
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test 1: Luxury velvet sofa under budget
    test_smart_search("luxury velvet sofa under $300")
    
    print("\n" + "=" * 70 + "\n")
    
    # Test 2: Italian leather sofa
    test_smart_search("Italian leather sofa under $400")
    
    print("\n" + "=" * 70 + "\n")
    
    # Test 3: Should find direct matches
    test_smart_search("dining table under $1000")

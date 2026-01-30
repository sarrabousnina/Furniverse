"""
Comprehensive test for "blue sofa" search
Tests all endpoints and vector embeddings
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_endpoint(endpoint, query, method="POST"):
    """Test a recommendation endpoint"""
    print(f"\n🔍 Testing: {endpoint}")
    print(f"Query: '{query}'\n")
    
    try:
        if method == "POST":
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json={"query": query, "limit": 5}
            )
        else:
            response = requests.get(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if it's a list or dict response
            products = data if isinstance(data, list) else data.get('products', [])
            
            if not products:
                print("❌ No products returned!")
                return False
            
            print(f"✅ Returned {len(products)} products:\n")
            
            has_blue = False
            for i, p in enumerate(products[:5], 1):
                name = p.get('name', 'Unknown')
                colors = p.get('colors', [])
                score = p.get('score', 0)
                
                # Check for blue
                is_blue = any('blue' in str(c).lower() for c in colors)
                if is_blue:
                    has_blue = True
                
                color_marker = "🔵" if is_blue else "⚪"
                print(f"{i}. {color_marker} {name}")
                print(f"   Colors: {', '.join(colors) if colors else 'None'}")
                
                if isinstance(data, dict):
                    # Show vector scores if available
                    if 'text_clip_score' in p:
                        print(f"   📊 text_clip: {p.get('text_clip_score', 0):.4f}, "
                              f"image_clip: {p.get('image_clip_score', 0):.4f}, "
                              f"color: {p.get('color_score', 0):.4f}")
                    print(f"   Score: {score:.4f}")
                print()
            
            if has_blue:
                print("✅ SUCCESS: Found blue products!")
                return True
            else:
                print("❌ FAILURE: No blue products in results!")
                return False
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def check_csv_data():
    """Check if blue products exist in the CSV"""
    print_header("CHECKING CSV DATA")
    
    try:
        import pandas as pd
        from pathlib import Path
        
        csv_path = Path(__file__).parent.parent / "Data" / "processed" / "products.csv"
        df = pd.read_csv(csv_path)
        
        # Find blue products
        blue_products = df[df['colors'].str.contains('blue', case=False, na=False)]
        
        print(f"\n📊 Total products in CSV: {len(df)}")
        print(f"🔵 Blue products in CSV: {len(blue_products)}")
        
        if len(blue_products) > 0:
            print("\n✅ Sample blue products:")
            for idx, row in blue_products.head(5).iterrows():
                print(f"  • {row['name']} - Colors: {row['colors']}")
            return True
        else:
            print("\n❌ No blue products found in CSV!")
            return False
            
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False


def main():
    print_header("BLUE SOFA SEARCH TEST")
    print("Testing all endpoints to find why 'blue sofa' doesn't return blue products\n")
    
    # Step 1: Check CSV data
    csv_ok = check_csv_data()
    
    if not csv_ok:
        print("\n⚠️ WARNING: No blue products in CSV - embeddings can't find what doesn't exist!")
        return
    
    # Step 2: Test all endpoints
    print_header("TESTING API ENDPOINTS")
    
    results = {}
    
    # Test /recommend/text
    results['text'] = test_endpoint("/recommend/text", "blue sofa")
    
    # Test /recommend/smart
    results['smart'] = test_endpoint("/recommend/smart", "blue sofa")
    
    # Test /recommend/fusion
    results['fusion'] = test_endpoint("/recommend/fusion", "blue sofa")
    
    # Summary
    print_header("SUMMARY")
    print("\nEndpoint Results:")
    for endpoint, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {endpoint:15s} {status}")
    
    # Diagnosis
    print("\n" + "=" * 80)
    print("DIAGNOSIS:")
    print("=" * 80)
    
    if all(results.values()):
        print("✅ All endpoints working correctly!")
    elif any(results.values()):
        print("⚠️ Mixed results - some endpoints work, others don't")
        print("\nWorking endpoints:")
        for endpoint, success in results.items():
            if success:
                print(f"  • {endpoint}")
        print("\nFailing endpoints:")
        for endpoint, success in results.items():
            if not success:
                print(f"  • {endpoint}")
    else:
        print("❌ CRITICAL: All endpoints failing!")
        print("\nPossible causes:")
        print("  1. Text embeddings don't include color information")
        print("  2. CLIP model not understanding 'blue' color concept")
        print("  3. Index not updated after code changes")
        print("  4. Vector weights incorrectly balanced")
        print("\n💡 Solution: Re-run indexing with updated embedding code")
        print("   cd Pipeline && python run_indexing.py")


if __name__ == "__main__":
    main()

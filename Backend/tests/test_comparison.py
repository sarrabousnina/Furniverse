"""
Quick test script for product comparison
Run this to verify the API is working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_comparison():
    """Test the product comparison endpoint"""
    
    print("🧪 Testing AI Product Comparison API...")
    print("=" * 50)
    
    # Test data - use actual product IDs from your database
    test_cases = [
        {"product_a_id": 1, "product_b_id": 2, "name": "Similar products"},
        {"product_a_id": 1, "product_b_id": 50, "name": "Different categories"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test['name']}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{BASE_URL}/compare/products",
                json={
                    "product_a_id": test["product_a_id"],
                    "product_b_id": test["product_b_id"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Success!")
                print(f"\n📍 Products:")
                print(f"  A: {data['product_a']['name']} (${data['product_a']['price']})")
                print(f"  B: {data['product_b']['name']} (${data['product_b']['price']})")
                
                print(f"\n🎨 Visual Similarity:")
                print(f"  Score: {data['visual_similarity']['score'] * 100:.1f}%")
                print(f"  Verdict: {data['visual_similarity']['verdict']}")
                
                print(f"\n💰 Price Analysis:")
                print(f"  {data['price_analysis']['verdict']}")
                
                print(f"\n🤖 AI Recommendation:")
                print(f"  Confidence: {data['ai_recommendation']['confidence']}%")
                print(f"  {data['ai_recommendation']['recommendation']}")
                
                print(f"\n✨ Reasons for Product A:")
                for reason in data['ai_recommendation']['reasons_for_a'][:3]:
                    print(f"    ✓ {reason}")
                
                print(f"\n✨ Reasons for Product B:")
                for reason in data['ai_recommendation']['reasons_for_b'][:3]:
                    print(f"    ✓ {reason}")
                
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is the backend running?")
            print("   Run: cd Backend && uv run uvicorn main:app --reload")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Testing complete!")
    print("\n💡 Next steps:")
    print("   1. Start frontend: cd Frontend && npm run dev")
    print("   2. Visit: http://localhost:5173/shop")
    print("   3. Click ⚖️ on two products")
    print("   4. Click 'Compare with AI'")
    print("   5. Show the jury! 🏆")

if __name__ == "__main__":
    test_comparison()

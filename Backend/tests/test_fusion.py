"""
Test multimodal fusion search
"""

import requests

BASE_URL = "http://localhost:8000"

def test_fusion(query):
    print("=" * 80)
    print(f"🔬 MULTIMODAL FUSION SEARCH")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    response = requests.post(
        f"{BASE_URL}/recommend/fusion",
        json={"query": query, "limit": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"⚡ Strategy: {data['strategy']}")
        print(f"\n🎯 Fusion Weights:")
        for key, weight in data['fusion_weights'].items():
            print(f"   • {key}: {weight*100:.0f}%")
        
        print(f"\n💬 Explanation:")
        print(f"   {data['explanation']}")
        
        if data.get('budget_limit'):
            print(f"\n💰 Budget: ${data['budget_limit']}")
        
        print(f"\n✨ Top {len(data['products'])} Products (Ranked by Fusion Score):\n")
        
        for i, p in enumerate(data['products'], 1):
            print(f"{i}. {p['name']}")
            print(f"   💵 Price: ${p['price']}")
            print(f"   📊 Fusion Score: {p['score']:.4f}")
            print(f"      ├─ CLIP (semantic): {p['clip_score']:.4f}")
            print(f"      └─ Graph (style): {p['graph_score']:.4f}")
            print(f"   🏷️  Category: {p['category']}")
            
            if p.get('tags'):
                print(f"   🔖 Tags: {', '.join(p['tags'][:4])}")
            
            if p.get('colors'):
                print(f"   🎨 Colors: {', '.join(p['colors'][:3])}")
            
            print()
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test 1: Luxury velvet sofa with budget
    test_fusion("luxury velvet sofa under $300")
    
    print("\n" + "=" * 80 + "\n")
    
    # Test 2: Modern minimalist furniture
    test_fusion("modern minimalist dining table under $500")
    
    print("\n" + "=" * 80 + "\n")
    
    # Test 3: Without budget constraint
    test_fusion("comfortable reading chair")

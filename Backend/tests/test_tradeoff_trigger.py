"""
Test query specifically designed to trigger trade-off alternatives
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_tradeoff_query(query, expected_budget=None):
    """Test a query that should trigger trade-offs"""
    print(f"\n{'='*80}")
    print(f"  Testing: '{query}'")
    if expected_budget:
        print(f"  Expected Budget: ${expected_budget}")
    print('='*80)
    
    response = requests.post(
        f"{BASE_URL}/recommend/smart",
        json={"query": query}
    )
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    exact = data.get('products', [])
    close = data.get('close_alternatives', [])
    premium = data.get('premium_alternatives', [])
    
    print(f"\n📊 RESULTS:")
    print(f"   Exact matches: {len(exact)}")
    print(f"   Close alternatives (+10-20% over): {len(close)}")
    print(f"   Premium alternatives (+20-30% over): {len(premium)}")
    
    if exact:
        print(f"\n✅ EXACT MATCHES:")
        for i, p in enumerate(exact[:5], 1):
            print(f"   {i}. {p['name']} - ${p['price']} (score: {p.get('score', 0):.4f})")
    
    if close:
        print(f"\n💡 CLOSE ALTERNATIVES (+10-20% over budget):")
        for i, p in enumerate(close[:5], 1):
            overage = ((p['price'] - expected_budget) / expected_budget * 100) if expected_budget else 0
            print(f"   {i}. {p['name']} - ${p['price']} (+{overage:.0f}% over)")
            print(f"      Original score: {p.get('original_score', 0):.4f}, Trade-off score: {p.get('trade_off_score', 0):.4f}")
    
    if premium:
        print(f"\n⭐ PREMIUM ALTERNATIVES (+20-30% over budget):")
        for i, p in enumerate(premium[:5], 1):
            overage = ((p['price'] - expected_budget) / expected_budget * 100) if expected_budget else 0
            print(f"   {i}. {p['name']} - ${p['price']} (+{overage:.0f}% over)")
            print(f"      Original score: {p.get('original_score', 0):.4f}, Trade-off score: {p.get('trade_off_score', 0):.4f}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  TRADE-OFF TRIGGER TESTING")
    print("="*80)
    print("\nTesting queries designed to trigger trade-off alternatives...")
    print("These have restrictive requirements that limit within-budget options.")
    
    # Very restrictive budget for blue sofas (KIVIK blue is $949)
    test_tradeoff_query("blue sofa under 600", expected_budget=600)
    input("\nPress Enter for next test...")
    
    # Specific material + low budget (leather sofas are typically $800+)
    test_tradeoff_query("leather sofa under 400", expected_budget=400)
    input("\nPress Enter for next test...")
    
    # Premium style + tight budget
    test_tradeoff_query("modern sectional sofa under 800", expected_budget=800)
    input("\nPress Enter for next test...")
    
    # Specific color + furniture type + low budget
    test_tradeoff_query("blue velvet chair under 200", expected_budget=200)
    
    print("\n" + "="*80)
    print("  TEST COMPLETE")
    print("="*80)
    print("\nIf you see close_alternatives or premium_alternatives above,")
    print("the trade-off system is working correctly!")
    print("\nIf still showing 0 alternatives, it means:")
    print("  1. Not enough high-similarity products exist over budget")
    print("  2. The candidate pool (50) doesn't contain over-budget matches")
    print("  3. May need to increase candidate pool size for trade-off discovery")

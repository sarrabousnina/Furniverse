"""
Test trade-off explanations to validate that we're providing clear reasoning
for why over-budget alternatives are being suggested
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_query_with_explanations(query, budget):
    """Test a query and show detailed trade-off explanations"""
    print(f"\n{'='*80}")
    print(f"  Testing: '{query}' with budget ${budget}")
    print('='*80)
    
    response = requests.post(
        f"{BASE_URL}/recommend/smart",
        json={"query": query, "max_price": budget}
    )
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    perfect = data.get('perfect_matches', [])
    over_budget = data.get('over_budget_options', [])
    alternatives = data.get('alternative_options', [])
    
    print(f"\n📊 RESULTS:")
    print(f"   ✅ Perfect matches (≥0.67 + within budget): {len(perfect)}")
    print(f"   💰 Over-budget options (≥0.67 + over budget): {len(over_budget)}")
    print(f"   🔄 Alternative options (0.63-0.67 similarity): {len(alternatives)}")
    
    # Show best perfect matches
    if perfect:
        print(f"\n✅ PERFECT MATCHES (≥0.67 similarity + within budget):")
        for i, p in enumerate(perfect[:3], 1):
            colors = ', '.join(p.get('colors', [])) if p.get('colors') else 'N/A'
            compromise = p.get('compromise', {})
            print(f"   {i}. {p['name']}")
            print(f"      💰 ${p['price']} | 🎯 {p['score']:.4f} | 🎨 {colors}")
            if compromise:
                print(f"      📝 {compromise.get('summary', '')}")
                if compromise.get('advantages'):
                    print(f"      ✨ Advantages: {', '.join(compromise['advantages'][:2])}")
    
    # Show over-budget options with explanations
    if over_budget:
        print(f"\n💰 OVER-BUDGET OPTIONS (≥0.67 similarity, but over budget):")
        print("   High-quality matches that cost more - see if they're worth it")
        print()
        for i, p in enumerate(over_budget[:3], 1):
            colors = ', '.join(p.get('colors', [])) if p.get('colors') else 'N/A'
            compromise = p.get('compromise', {})
            
            print(f"   {i}. {p['name']}")
            print(f"      💰 ${p['price']} | 🎯 {p['score']:.4f} | 🎨 {colors}")
            
            if compromise:
                print(f"\n      📝 TRADE-OFF ANALYSIS:")
                print(f"         {compromise.get('summary', '')}")
                
                advantages = compromise.get('advantages', [])
                if advantages:
                    print(f"\n      ✨ ADVANTAGES:")
                    for adv in advantages[:3]:
                        print(f"         • {adv}")
                
                disadvantages = compromise.get('disadvantages', [])
                if disadvantages:
                    print(f"\n      ⚠️  DISADVANTAGES:")
                    for dis in disadvantages[:3]:
                        print(f"         • {dis}")
            print()
    
    # Show alternative options
    if alternatives:
        print(f"\n🔄 ALTERNATIVE OPTIONS (0.63-0.67 similarity - lower match):")
        print("   Different compromises - each shows what you gain/lose")
        print()
        for i, p in enumerate(alternatives[:3], 1):
            colors = ', '.join(p.get('colors', [])) if p.get('colors') else 'N/A'
            compromise = p.get('compromise', {})
            
            print(f"   {i}. {p['name']}")
            print(f"      💰 ${p['price']} | 🎯 {p['score']:.4f} | 🎨 {colors}")
            
            if compromise:
                print(f"\n      📝 TRADE-OFF ANALYSIS:")
                print(f"         {compromise.get('summary', '')}")
                
                advantages = compromise.get('advantages', [])
                if advantages:
                    print(f"\n      ✨ ADVANTAGES:")
                    for adv in advantages[:3]:
                        print(f"         • {adv}")
                
                disadvantages = compromise.get('disadvantages', [])
                if disadvantages:
                    print(f"\n      ⚠️  DISADVANTAGES:")
                    for dis in disadvantages[:3]:
                        print(f"         • {dis}")
            print()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  TRADE-OFF EXPLANATION TESTING")
    print("="*80)
    print("\nValidating that over-budget alternatives come with clear explanations")
    print("showing advantages, disadvantages, and why they cost more.")
    print("\nMinimum similarity threshold: 0.67 (67%) - below this = different product category")
    print("(e.g., won't show TV units when searching for sofas)")
    
    # Test 1: Blue sofa with restrictive budget
    test_query_with_explanations("blue sofa under 600", 600)
    input("\nPress Enter for next test...")
    
    # Test 2: Leather sofa with very low budget
    test_query_with_explanations("leather sofa under 400", 400)
    input("\nPress Enter for next test...")
    
    # Test 3: Modern sectional with moderate budget
    test_query_with_explanations("modern sectional sofa under 800", 800)
    input("\nPress Enter for next test...")
    
    # Test 4: Premium search
    test_query_with_explanations("blue velvet chair under 200", 200)
    
    print("\n" + "="*80)
    print("  VALIDATION COMPLETE")
    print("="*80)
    print("\n✅ Check that:")
    print("   1. All alternatives have similarity ≥ 0.67 (same product category)")
    print("   2. Explanations clearly state why products cost more")
    print("   3. Advantages are specific (size, quality, features, color match)")
    print("   4. Disadvantages include price difference and percentage")
    print("   5. Summary provides actionable insight")
    print("   6. No TV units when searching for sofas, no sofas when searching for chairs")

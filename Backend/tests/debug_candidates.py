"""
Debug script to see what candidates are returned and why trade-offs aren't triggering
"""
import requests
import json

def debug_query(query, budget):
    """Show all 50 candidates and calculate what tier they'd fall into"""
    print(f"\n{'='*80}")
    print(f"  DEBUGGING: '{query}' with budget ${budget}")
    print('='*80)
    
    # Get the raw smart search response
    response = requests.post(
        "http://localhost:8000/recommend/smart",
        json={"query": query, "max_price": budget}
    )
    
    data = response.json()
    exact = data.get('products', [])
    close = data.get('close_alternatives', [])
    premium = data.get('premium_alternatives', [])
    
    print(f"\n📊 RETURNED RESULTS:")
    print(f"   Exact: {len(exact)}, Close: {len(close)}, Premium: {len(premium)}")
    
    # Now get ALL candidates without budget filter to see what exists
    response_no_budget = requests.post(
        "http://localhost:8000/recommend/text",
        json={"query": query, "limit": 50}
    )
    
    all_candidates = response_no_budget.json()
    
    print(f"\n🔍 ALL 50 CANDIDATES (sorted by similarity):")
    print(f"{'Rank':<6}{'Name':<40}{'Price':<10}{'Score':<10}{'Budget Status':<30}")
    print('-'*96)
    
    within_budget = 0
    over_10 = 0
    over_20 = 0
    over_30 = 0
    over_50 = 0
    way_over = 0
    
    for i, prod in enumerate(all_candidates[:50], 1):
        name = prod['name'][:37] + "..." if len(prod['name']) > 37 else prod['name']
        price = prod['price']
        score = prod['score']
        
        if price <= budget:
            status = "✅ WITHIN BUDGET"
            within_budget += 1
        else:
            overage = ((price - budget) / budget) * 100
            if overage <= 10:
                status = f"💡 +{overage:.0f}% (TIER 1)"
                over_10 += 1
            elif overage <= 20:
                status = f"💡 +{overage:.0f}% (TIER 2)"
                over_20 += 1
            elif overage <= 30:
                status = f"⭐ +{overage:.0f}% (TIER 3)"
                over_30 += 1
            elif overage <= 50:
                status = f"⚠️ +{overage:.0f}% (50% over)"
                over_50 += 1
            else:
                status = f"❌ +{overage:.0f}% (WAY OVER)"
                way_over += 1
        
        print(f"{i:<6}{name:<40}${price:<9.0f}{score:<10.4f}{status:<30}")
    
    print(f"\n📈 CANDIDATE DISTRIBUTION:")
    print(f"   Within budget: {within_budget}")
    print(f"   +10% over (Tier 1): {over_10}")
    print(f"   +20% over (Tier 2): {over_20}")
    print(f"   +30% over (Tier 3): {over_30}")
    print(f"   +50% over: {over_50}")
    print(f"   >50% over: {way_over}")
    
    print(f"\n💭 ANALYSIS:")
    if over_10 == 0 and over_20 == 0 and over_30 == 0:
        print("   ⚠️ NO products in 10-30% range!")
        if over_50 > 0 or way_over > 0:
            print(f"   🔧 Need to increase tier percentages to 50%+ to capture alternatives")
        else:
            print(f"   ✅ Budget is generous enough that {within_budget} products fit within it")
    else:
        print(f"   🎯 {over_10 + over_20 + over_30} products fall in trade-off range")
        print(f"   🔍 Check similarity scores - need 0.65+ for Tier1, 0.70+ for Tier2, 0.75+ for Tier3")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  CANDIDATE POOL DEBUGGING")
    print("="*80)
    print("\nAnalyzing what products are in the candidate pool and why trade-offs don't trigger...")
    
    debug_query("blue sofa under 600", 600)
    input("\nPress Enter for next...")
    
    debug_query("leather sofa under 400", 400)
    input("\nPress Enter for next...")
    
    debug_query("modern sectional sofa under 800", 800)
    
    print("\n" + "="*80)
    print("  DEBUGGING COMPLETE")
    print("="*80)

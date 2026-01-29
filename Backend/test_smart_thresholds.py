"""
Test script for tuning smart search hyperparameters

This script helps you test different threshold values and see how they affect results.
Use this to find the optimal balance between result quality and quantity.
"""

import requests
import json
from typing import Dict, List

BASE_URL = "http://localhost:8000"

# TEST QUERIES with different characteristics
TEST_QUERIES = [
    # Color-specific queries
    ("blue sofa", None, "Should return blue sofas with dynamic thresholds"),
    ("red chair", None, "Should filter by color + dynamic quality"),
    
    # Budget queries
    ("sofa under 500", 500, "Should show within budget + trade-offs"),
    ("leather sofa under 800", 800, "Should handle material + budget"),
    ("dining table under 300", 300, "Low budget - test trade-off tiers"),
    
    # No budget queries
    ("modern sofa", None, "Should use similarity-only filtering"),
    ("velvet chair", None, "Should show all quality matches"),
]

def print_separator(title=""):
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()

def test_query(query: str, expected_budget: float = None, description: str = ""):
    """Test a single query and analyze the results"""
    print_separator(f"Testing: '{query}'")
    print(f"📝 Description: {description}")
    if expected_budget:
        print(f"💰 Expected Budget: ${expected_budget}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/recommend/smart",
            json={"query": query, "limit": 8}
        )
        
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            return None
        
        data = response.json()
        
        # Extract results
        exact_matches = data.get('products', [])
        close_alternatives = data.get('close_alternatives', [])
        premium_alternatives = data.get('premium_alternatives', [])
        
        print(f"\n📊 RESULTS BREAKDOWN:")
        print(f"   Strategy: {data.get('strategy', 'N/A')}")
        print(f"   Explanation: {data.get('explanation', 'N/A')}")
        
        if 'thresholds_used' in data:
            thresholds = data['thresholds_used']
            print(f"\n🎯 THRESHOLDS USED:")
            print(f"   Excellent: {thresholds.get('excellent', 'N/A')}")
            print(f"   Good: {thresholds.get('good', 'N/A')}")
            print(f"   Fair: {thresholds.get('fair', 'N/A')}")
            print(f"   Minimum: {thresholds.get('minimum', 'N/A')}")
        
        # Show exact matches
        if exact_matches:
            print(f"\n✅ EXACT MATCHES ({len(exact_matches)}):")
            for i, p in enumerate(exact_matches[:5], 1):
                print(f"   {i}. {p.get('name', 'Unknown')}")
                print(f"      Score: {p.get('score', 0):.4f} | Price: ${p.get('price', 0)} | Colors: {', '.join(p.get('colors', []))}")
        else:
            print(f"\n✅ EXACT MATCHES: None")
        
        # Show close alternatives
        if close_alternatives:
            print(f"\n💡 CLOSE ALTERNATIVES ({len(close_alternatives)}):")
            for i, p in enumerate(close_alternatives[:3], 1):
                print(f"   {i}. {p.get('name', 'Unknown')}")
                print(f"      Original Score: {p.get('original_score', 0):.4f} | Trade-off Score: {p.get('trade_off_score', 0):.4f}")
                print(f"      Price: ${p.get('price', 0)} (+${p.get('price_overage', 0)}, {p.get('price_overage_percent', 0):.1f}% over)")
        else:
            print(f"\n💡 CLOSE ALTERNATIVES: None")
        
        # Show premium alternatives
        if premium_alternatives:
            print(f"\n⭐ PREMIUM ALTERNATIVES ({len(premium_alternatives)}):")
            for i, p in enumerate(premium_alternatives[:3], 1):
                print(f"   {i}. {p.get('name', 'Unknown')}")
                print(f"      Original Score: {p.get('original_score', 0):.4f} | Trade-off Score: {p.get('trade_off_score', 0):.4f}")
                print(f"      Price: ${p.get('price', 0)} (+${p.get('price_overage', 0)}, {p.get('price_overage_percent', 0):.1f}% over)")
        else:
            print(f"\n⭐ PREMIUM ALTERNATIVES: None")
        
        # Quality analysis
        total_results = len(exact_matches) + len(close_alternatives) + len(premium_alternatives)
        print(f"\n📈 QUALITY METRICS:")
        print(f"   Total Results: {total_results}")
        
        if exact_matches:
            avg_score = sum(p.get('score', 0) for p in exact_matches) / len(exact_matches)
            min_score = min(p.get('score', 0) for p in exact_matches)
            max_score = max(p.get('score', 0) for p in exact_matches)
            print(f"   Exact Match Scores: avg={avg_score:.4f}, min={min_score:.4f}, max={max_score:.4f}")
        
        if close_alternatives:
            avg_tradeoff = sum(p.get('trade_off_score', 0) for p in close_alternatives) / len(close_alternatives)
            avg_overage = sum(p.get('price_overage_percent', 0) for p in close_alternatives) / len(close_alternatives)
            print(f"   Close Alt Trade-offs: avg_score={avg_tradeoff:.4f}, avg_overage={avg_overage:.1f}%")
        
        return {
            'query': query,
            'exact': len(exact_matches),
            'close': len(close_alternatives),
            'premium': len(premium_alternatives),
            'total': total_results,
            'strategy': data.get('strategy')
        }
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def main():
    """Run all test queries and generate summary"""
    print_separator("SMART SEARCH THRESHOLD TESTING")
    print("Testing dynamic similarity thresholds and budget-aware trade-offs")
    print("\nCurrent hyperparameters (TUNED v2 - Real Furniture Pricing):")
    print("  - THRESHOLD_EXCELLENT = 0.70")
    print("  - THRESHOLD_GOOD = 0.60")
    print("  - THRESHOLD_FAIR = 0.50")
    print("  - THRESHOLD_MINIMUM = 0.40")
    print("  - BUDGET_TIER_1_PERCENT = 25%  (min similarity 0.67 - close alternatives)")
    print("  - BUDGET_TIER_2_PERCENT = 60%  (min similarity 0.69 - premium alternatives)")
    print("\nRationale: Furniture has natural price tiers ($500, $1000, $1500) not incremental pricing.")
    print("          Show alternatives only when similarity justifies the price jump.")
    print("          Minimum 0.67 to stay within same product category (no TV units for sofas).")
    
    results = []
    
    for query, budget, description in TEST_QUERIES:
        result = test_query(query, budget, description)
        if result:
            results.append(result)
        input("\nPress Enter to continue to next test...")
    
    # Generate summary
    print_separator("SUMMARY")
    print(f"Tested {len(results)} queries\n")
    
    for r in results:
        print(f"'{r['query']}':")
        print(f"  Strategy: {r['strategy']}")
        print(f"  Results: {r['exact']} exact + {r['close']} close + {r['premium']} premium = {r['total']} total")
        print()
    
    # Recommendations
    print_separator("TUNING RECOMMENDATIONS")
    print("Based on the results above, consider adjusting:")
    print()
    print("If too many results:")
    print("  - Increase THRESHOLD_EXCELLENT (0.70 → 0.75)")
    print("  - Increase THRESHOLD_GOOD (0.60 → 0.65)")
    print()
    print("If too few results:")
    print("  - Decrease THRESHOLD_FAIR (0.50 → 0.45)")
    print("  - Decrease THRESHOLD_MINIMUM (0.40 → 0.35)")
    print()
    print("If trade-offs seem too expensive:")
    print("  - Decrease BUDGET_TIER_1_PERCENT (10% → 8%)")
    print("  - Increase TRADEOFF_MIN_SIMILARITY_TIER_1 (0.75 → 0.80)")
    print()
    print("If trade-offs are good but need more:")
    print("  - Increase BUDGET_TIER_2_PERCENT (20% → 25%)")
    print("  - Decrease TRADEOFF_MIN_SIMILARITY_TIER_2 (0.80 → 0.75)")


if __name__ == "__main__":
    main()

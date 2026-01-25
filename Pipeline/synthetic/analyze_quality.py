"""
Quality Analysis for Synthetic Data
Evaluates the generated users, purchases, and interactions for realism and consistency.
"""

import json
import numpy as np
from collections import Counter
from datetime import datetime


def load_data():
    """Load all synthetic datasets."""
    with open("../../Data/processed/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)
    with open("../../Data/processed/purchases.json", "r", encoding="utf-8") as f:
        purchases = json.load(f)
    with open("../../Data/processed/interactions.json", "r", encoding="utf-8") as f:
        interactions = json.load(f)
    with open("../../Data/raw/products.json", "r", encoding="utf-8") as f:
        products = json.load(f)
    return users, purchases, interactions, products


def analyze_users(users):
    """Analyze user data quality."""
    print("\n" + "="*60)
    print("USER QUALITY ANALYSIS")
    print("="*60)
    
    print(f"\nTotal Users: {len(users)}")
    
    # Budget tier distribution
    budget_tiers = Counter(u["budget_tier"] for u in users)
    print(f"\nBudget Tier Distribution:")
    for tier, count in sorted(budget_tiers.items()):
        pct = count / len(users) * 100
        print(f"  {tier}: {count} ({pct:.1f}%)")
    
    # Room distribution
    all_rooms = []
    for u in users:
        all_rooms.extend(u["rooms"])
    room_counts = Counter(all_rooms)
    print(f"\nRoom Type Distribution:")
    for room, count in room_counts.most_common():
        print(f"  {room}: {count}")
    
    # Rooms per user
    rooms_per_user = [len(u["rooms"]) for u in users]
    print(f"\nRooms per User:")
    print(f"  Mean: {np.mean(rooms_per_user):.2f}")
    print(f"  Min: {min(rooms_per_user)}, Max: {max(rooms_per_user)}")
    
    # Centroid validation
    centroid_norms = [np.linalg.norm(u["centroid"]) for u in users]
    print(f"\nCentroid Quality:")
    print(f"  Mean norm: {np.mean(centroid_norms):.4f} (should be ~1.0)")
    print(f"  Std norm: {np.std(centroid_norms):.4f}")
    print(f"  Dimension: {len(users[0]['centroid'])}")


def analyze_purchases(purchases, users, products):
    """Analyze purchase data quality."""
    print("\n" + "="*60)
    print("PURCHASE QUALITY ANALYSIS")
    print("="*60)
    
    print(f"\nTotal Purchases: {len(purchases)}")
    
    # Purchases per user
    purchases_per_user = Counter(p["user_id"] for p in purchases)
    ppu_values = list(purchases_per_user.values())
    print(f"\nPurchases per User:")
    print(f"  Mean: {np.mean(ppu_values):.2f}")
    print(f"  Median: {np.median(ppu_values):.2f}")
    print(f"  Min: {min(ppu_values)}, Max: {max(ppu_values)}")
    print(f"  Std: {np.std(ppu_values):.2f}")
    
    # Distribution histogram
    ppu_dist = Counter(ppu_values)
    print(f"\n  Distribution:")
    for count in sorted(ppu_dist.keys()):
        bar = "█" * (ppu_dist[count] // 10)
        print(f"    {count} purchases: {ppu_dist[count]:4d} users {bar}")
    
    # Similarity score analysis
    sim_scores = [p["similarity_score"] for p in purchases]
    print(f"\nSimilarity Scores:")
    print(f"  Mean: {np.mean(sim_scores):.4f}")
    print(f"  Median: {np.median(sim_scores):.4f}")
    print(f"  Std: {np.std(sim_scores):.4f}")
    print(f"  Min: {min(sim_scores):.4f}, Max: {max(sim_scores):.4f}")
    
    # Percentiles
    percentiles = [10, 25, 50, 75, 90]
    print(f"\n  Percentiles:")
    for p in percentiles:
        val = np.percentile(sim_scores, p)
        print(f"    P{p}: {val:.4f}")
    
    # Low similarity analysis
    low_sim = [s for s in sim_scores if s < 0.1]
    print(f"\n  Low similarity (<0.1): {len(low_sim)} ({len(low_sim)/len(sim_scores)*100:.1f}%)")
    
    # Category distribution
    categories = Counter(p["category"] for p in purchases)
    print(f"\nCategory Distribution:")
    for cat, count in categories.most_common(10):
        pct = count / len(purchases) * 100
        print(f"  {cat}: {count} ({pct:.1f}%)")
    
    # Price analysis
    prices = [p["price_paid"] for p in purchases]
    print(f"\nPrice Distribution:")
    print(f"  Mean: ${np.mean(prices):.2f}")
    print(f"  Median: ${np.median(prices):.2f}")
    print(f"  Min: ${min(prices):.2f}, Max: ${max(prices):.2f}")
    
    # Referential integrity
    user_ids = set(u["user_id"] for u in users)
    product_ids = set(p["id"] for p in products)
    
    invalid_users = [p for p in purchases if p["user_id"] not in user_ids]
    invalid_products = [p for p in purchases if p["product_id"] not in product_ids]
    
    print(f"\nReferential Integrity:")
    print(f"  Invalid user_ids: {len(invalid_users)}")
    print(f"  Invalid product_ids: {len(invalid_products)}")


def analyze_interactions(interactions, users, products, purchases):
    """Analyze interaction data quality."""
    print("\n" + "="*60)
    print("INTERACTION QUALITY ANALYSIS")
    print("="*60)
    
    print(f"\nTotal Interactions: {len(interactions)}")
    
    # Action distribution
    actions = Counter(i["action"] for i in interactions)
    print(f"\nAction Distribution:")
    for action, count in actions.most_common():
        pct = count / len(interactions) * 100
        print(f"  {action}: {count} ({pct:.1f}%)")
    
    # Expected funnel ratio (views > clicks > add_to_cart)
    print(f"\n  Funnel Ratio Check:")
    if actions["view"] > actions["click"] > actions["add_to_cart"]:
        print(f"    ✓ Correct funnel: views > clicks > add_to_cart")
    else:
        print(f"    ✗ Funnel violation detected")
    
    # Interactions per user
    ipu = Counter(i["user_id"] for i in interactions)
    ipu_values = list(ipu.values())
    print(f"\nInteractions per User:")
    print(f"  Mean: {np.mean(ipu_values):.2f}")
    print(f"  Median: {np.median(ipu_values):.2f}")
    print(f"  Min: {min(ipu_values)}, Max: {max(ipu_values)}")
    
    # Similarity by action type
    print(f"\nSimilarity by Action Type:")
    for action in ["view", "click", "add_to_cart"]:
        action_sims = [i["similarity"] for i in interactions if i["action"] == action]
        if action_sims:
            print(f"  {action}:")
            print(f"    Mean: {np.mean(action_sims):.4f}")
            print(f"    Median: {np.median(action_sims):.4f}")
    
    # Temporal analysis
    print(f"\nTemporal Analysis:")
    timestamps = [datetime.fromisoformat(i["timestamp"]) for i in interactions]
    date_range = (max(timestamps) - min(timestamps)).days
    print(f"  Date range: {date_range} days")
    print(f"  Earliest: {min(timestamps).date()}")
    print(f"  Latest: {max(timestamps).date()}")
    
    # Referential integrity
    user_ids = set(u["user_id"] for u in users)
    product_ids = set(p["id"] for p in products)
    
    invalid_users = [i for i in interactions if i["user_id"] not in user_ids]
    invalid_products = [i for i in interactions if i["product_id"] not in product_ids]
    
    print(f"\nReferential Integrity:")
    print(f"  Invalid user_ids: {len(invalid_users)}")
    print(f"  Invalid product_ids: {len(invalid_products)}")


def analyze_consistency(users, purchases, interactions):
    """Cross-dataset consistency analysis."""
    print("\n" + "="*60)
    print("CROSS-DATASET CONSISTENCY")
    print("="*60)
    
    # User coverage
    user_ids = set(u["user_id"] for u in users)
    users_with_purchases = set(p["user_id"] for p in purchases)
    users_with_interactions = set(i["user_id"] for i in interactions)
    
    print(f"\nUser Coverage:")
    print(f"  Total users: {len(user_ids)}")
    print(f"  Users with purchases: {len(users_with_purchases)} ({len(users_with_purchases)/len(user_ids)*100:.1f}%)")
    print(f"  Users with interactions: {len(users_with_interactions)} ({len(users_with_interactions)/len(user_ids)*100:.1f}%)")
    
    # Orphan check
    orphan_purchases = users_with_purchases - user_ids
    orphan_interactions = users_with_interactions - user_ids
    print(f"\n  Orphan user_ids in purchases: {len(orphan_purchases)}")
    print(f"  Orphan user_ids in interactions: {len(orphan_interactions)}")
    
    # Purchase-interaction link
    purchased_products = {}
    for p in purchases:
        key = (p["user_id"], p["product_id"])
        purchased_products[key] = p
    
    add_to_cart_interactions = [i for i in interactions if i["action"] == "add_to_cart"]
    linked_carts = 0
    for i in add_to_cart_interactions:
        if (i["user_id"], i["product_id"]) in purchased_products:
            linked_carts += 1
    
    print(f"\nPurchase-Interaction Linkage:")
    print(f"  Add-to-cart interactions: {len(add_to_cart_interactions)}")
    print(f"  Linked to purchases: {linked_carts} ({linked_carts/len(add_to_cart_interactions)*100:.1f}%)")


def main():
    print("\n" + "="*60)
    print("SYNTHETIC DATA QUALITY REPORT")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    users, purchases, interactions, products = load_data()
    
    analyze_users(users)
    analyze_purchases(purchases, users, products)
    analyze_interactions(interactions, users, products, purchases)
    analyze_consistency(users, purchases, interactions)
    
    print("\n" + "="*60)
    print("QUALITY SUMMARY")
    print("="*60)
    
    # Overall quality indicators
    issues = []
    
    # Check similarity scores
    sim_scores = [p["similarity_score"] for p in purchases]
    mean_sim = np.mean(sim_scores)
    if mean_sim < 0.15:
        issues.append(f"⚠ Low mean similarity score ({mean_sim:.4f}) - user preferences may not align well with purchases")
    
    # Check funnel
    actions = Counter(i["action"] for i in interactions)
    if not (actions["view"] > actions["click"] > actions["add_to_cart"]):
        issues.append("⚠ Funnel ratio violated")
    
    # Check coverage
    user_ids = set(u["user_id"] for u in users)
    users_with_purchases = set(p["user_id"] for p in purchases)
    if len(users_with_purchases) < len(user_ids) * 0.95:
        issues.append(f"⚠ Only {len(users_with_purchases)/len(user_ids)*100:.1f}% users have purchases")
    
    if issues:
        print("\nIssues Found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✓ All quality checks passed!")
    
    print(f"\nDataset Scale:")
    print(f"  Users: {len(users)}")
    print(f"  Purchases: {len(purchases)}")
    print(f"  Interactions: {len(interactions)}")
    print(f"  Products: {len(products)}")


if __name__ == "__main__":
    main()

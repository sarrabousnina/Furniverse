"""
Generate synthetic users with centroid-based preference vectors.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np


ROOM_TYPES = ['living_room', 'bedroom', 'dining_room', 'office', 'kitchen']
BUDGET_TIERS = {
    'low': (0, 300),
    'medium': (300, 800),
    'high': (800, 2000),
    'luxury': (2000, 10000)
}


def generate_user_centroids(products: List[Dict], embeddings: np.ndarray, num_users: int = 1000) -> List[Dict]:
    """Generate users with centroid-based preference vectors"""
    print(f"\nGenerating {num_users} users with vector centroids...")
    
    users = []
    
    for user_id in range(num_users):
        # Sample 5-15 random products to form initial preferences
        num_seed_products = random.randint(5, 15)
        seed_indices = random.sample(range(len(products)), num_seed_products)
        
        # Compute centroid (mean embedding)
        seed_embeddings = embeddings[seed_indices]
        centroid = np.mean(seed_embeddings, axis=0)
        
        # Add noise for diversity (10% noise)
        noise = np.random.randn(*centroid.shape) * 0.1
        centroid = centroid + noise
        centroid = centroid / np.linalg.norm(centroid)  # Normalize
        
        # Infer budget from seed products
        seed_prices = [products[i]['price'] for i in seed_indices]
        avg_price = np.mean(seed_prices)
        
        if avg_price < 300:
            budget_tier = 'low'
        elif avg_price < 800:
            budget_tier = 'medium'
        elif avg_price < 2000:
            budget_tier = 'high'
        else:
            budget_tier = 'luxury'
        
        # User rooms (1-3 active rooms)
        num_rooms = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
        rooms = random.sample(ROOM_TYPES, num_rooms)
        
        # Last active date (past 6 months)
        last_active = datetime.now() - timedelta(days=random.randint(0, 180))
        
        user = {
            'user_id': f'user_{user_id:04d}',
            'centroid': centroid.tolist(),  # Store for later use
            'budget_tier': budget_tier,
            'budget_min': BUDGET_TIERS[budget_tier][0],
            'budget_max': BUDGET_TIERS[budget_tier][1],
            'rooms': rooms,
            'last_active': last_active.strftime('%Y-%m-%d'),
            'created_at': (last_active - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
        }
        
        users.append(user)
    
    print(f"✓ Generated {len(users)} users")
    print(f"  Budget tiers: {sum(1 for u in users if u['budget_tier'] == 'low')} low, "
          f"{sum(1 for u in users if u['budget_tier'] == 'medium')} medium, "
          f"{sum(1 for u in users if u['budget_tier'] == 'high')} high, "
          f"{sum(1 for u in users if u['budget_tier'] == 'luxury')} luxury")
    
    return users

"""
Generate synthetic interactions (browsing funnel) based on similarity patterns.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def generate_interactions(users: List[Dict], products: List[Dict], purchases: List[Dict],
                         embeddings: np.ndarray, num_interactions: int = 20000) -> List[Dict]:
    """Generate realistic browsing funnel using similarity-based exploration"""
    print(f"\nGenerating {num_interactions} interactions...")
    
    interactions = []
    interaction_id = 0
    
    # For each purchase, generate a funnel
    for purchase in purchases:
        if interaction_id >= num_interactions:
            break
        
        user_id = purchase['user_id']
        product_id = purchase['product_id']
        purchase_date = datetime.strptime(purchase['purchase_date'], '%Y-%m-%d')
        
        # Find product index and embedding
        product_idx = next((i for i, p in enumerate(products) if str(p['id']) == product_id), None)
        if product_idx is None:
            continue
        
        product_embedding = embeddings[product_idx].reshape(1, -1)
        
        # Compute similarities to all products
        similarities = cosine_similarity(product_embedding, embeddings)[0]
        
        # Generate funnel events BEFORE purchase
        
        # 1. Views (5-10 similar products, similarity 0.5-0.8, 1-14 days before)
        num_views = random.randint(5, 10)
        view_candidates = np.where((similarities > 0.5) & (similarities < 0.8))[0]
        if len(view_candidates) > 0:
            for _ in range(min(num_views, len(view_candidates))):
                if interaction_id >= num_interactions:
                    break
                
                similar_idx = np.random.choice(view_candidates)
                view_date = purchase_date - timedelta(days=random.randint(1, 14), 
                                                       hours=random.randint(0, 23))
                
                interactions.append({
                    'interaction_id': f'int_{interaction_id:06d}',
                    'user_id': user_id,
                    'product_id': str(products[similar_idx]['id']),
                    'action': 'view',
                    'timestamp': view_date.strftime('%Y-%m-%dT%H:%M:%S'),
                    'similarity': float(similarities[similar_idx])
                })
                interaction_id += 1
        
        # 2. Clicks (2-4 products, higher similarity 0.7-0.9, closer to purchase)
        num_clicks = random.randint(2, 4)
        click_candidates = np.where((similarities > 0.7) & (similarities < 0.9))[0]
        if len(click_candidates) > 0:
            for _ in range(min(num_clicks, len(click_candidates))):
                if interaction_id >= num_interactions:
                    break
                
                similar_idx = np.random.choice(click_candidates)
                click_date = purchase_date - timedelta(days=random.randint(0, 7), 
                                                        hours=random.randint(0, 23))
                
                interactions.append({
                    'interaction_id': f'int_{interaction_id:06d}',
                    'user_id': user_id,
                    'product_id': str(products[similar_idx]['id']),
                    'action': 'click',
                    'timestamp': click_date.strftime('%Y-%m-%dT%H:%M:%S'),
                    'similarity': float(similarities[similar_idx])
                })
                interaction_id += 1
        
        # 3. Add to cart (actual product, 0-3 days before)
        if interaction_id < num_interactions:
            cart_date = purchase_date - timedelta(days=random.randint(0, 3), 
                                                   hours=random.randint(0, 23))
            
            interactions.append({
                'interaction_id': f'int_{interaction_id:06d}',
                'user_id': user_id,
                'product_id': product_id,
                'action': 'add_to_cart',
                'timestamp': cart_date.strftime('%Y-%m-%dT%H:%M:%S'),
                'similarity': 1.0
            })
            interaction_id += 1
    
    # Fill remaining with random browsing (exploration, no purchase)
    while interaction_id < num_interactions:
        user = random.choice(users)
        user_centroid = np.array(user['centroid']).reshape(1, -1)
        
        # Browse products similar to user preferences
        similarities = cosine_similarity(user_centroid, embeddings)[0]
        
        # 70% views (lower similarity), 30% clicks (higher similarity)
        if random.random() < 0.7:
            action = 'view'
            candidates = np.where(similarities > 0.3)[0]
        else:
            action = 'click'
            candidates = np.where(similarities > 0.5)[0]
        
        if len(candidates) > 0:
            product_idx = np.random.choice(candidates)
            days_ago = random.randint(0, 180)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            interactions.append({
                'interaction_id': f'int_{interaction_id:06d}',
                'user_id': user['user_id'],
                'product_id': str(products[product_idx]['id']),
                'action': action,
                'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                'similarity': float(similarities[product_idx])
            })
            interaction_id += 1
    
    print(f"✓ Generated {len(interactions)} interactions")
    action_counts = {}
    for i in interactions:
        action_counts[i['action']] = action_counts.get(i['action'], 0) + 1
    print(f"  Actions: {action_counts}")
    avg_sim = np.mean([i['similarity'] for i in interactions])
    print(f"  Avg similarity: {avg_sim:.3f}")
    
    return interactions

"""
Generate synthetic purchases based on cosine similarity to user centroids.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def generate_purchases(users: List[Dict], products: List[Dict], embeddings: np.ndarray, 
                       num_purchases: int = 3000) -> List[Dict]:
    """Generate purchases based on cosine similarity to user centroids"""
    print(f"\nGenerating {num_purchases} purchases using vector similarity...")
    
    purchases = []
    purchase_id = 0
    
    # Distribute purchases across users (Poisson-like)
    purchases_per_user = np.random.poisson(lam=3, size=len(users))
    purchases_per_user = np.clip(purchases_per_user, 1, 10)  # 1-10 purchases per user
    
    for user, num_user_purchases in zip(users, purchases_per_user):
        if purchase_id >= num_purchases:
            break
        
        user_centroid = np.array(user['centroid']).reshape(1, -1)
        user_last_active = datetime.strptime(user['last_active'], '%Y-%m-%d')
        
        # Compute similarities to all products
        similarities = cosine_similarity(user_centroid, embeddings)[0]
        
        # Filter by budget (with 20% flexibility)
        budget_max = user['budget_max'] * 1.2
        affordable_mask = np.array([p['price'] <= budget_max for p in products])
        
        # Zero out unaffordable products
        similarities = similarities * affordable_mask
        
        # Get top candidates (90% from top-100 similar, 10% exploration)
        for _ in range(int(num_user_purchases)):
            if purchase_id >= num_purchases:
                break
            
            if random.random() < 0.9:
                # Sample from top-100 with probability proportional to similarity
                top_k = min(100, len(products))
                top_indices = np.argsort(similarities)[-top_k:]
                top_similarities = similarities[top_indices]
                
                # Softmax for sampling probabilities
                probs = np.exp(top_similarities * 5)  # Temperature = 0.2
                probs = probs / probs.sum()
                
                product_idx = np.random.choice(top_indices, p=probs)
            else:
                # Random exploration
                affordable_indices = np.where(affordable_mask)[0]
                if len(affordable_indices) == 0:
                    continue
                product_idx = np.random.choice(affordable_indices)
            
            product = products[product_idx]
            
            # Purchase date (within last 6 months, before last_active)
            days_ago = random.randint(1, 180)
            purchase_date = user_last_active - timedelta(days=days_ago)
            
            purchase = {
                'purchase_id': f'purchase_{purchase_id:05d}',
                'user_id': user['user_id'],
                'product_id': str(product['id']),
                'price_paid': product['price'],
                'purchase_date': purchase_date.strftime('%Y-%m-%d'),
                'category': product['category'],
                'similarity_score': float(similarities[product_idx])
            }
            
            purchases.append(purchase)
            purchase_id += 1
            
            # Zero out purchased item to avoid duplicates
            similarities[product_idx] = 0
    
    print(f"✓ Generated {len(purchases)} purchases")
    print(f"  Avg purchases per user: {len(purchases) / len(users):.1f}")
    print(f"  Avg similarity score: {np.mean([p['similarity_score'] for p in purchases]):.3f}")
    
    return purchases

"""
User and Room Profile Indexing for Furniverse

Creates rich user and room profiles for personalized recommendations:

User Profiles:
- Preference vector (aggregated CLIP embeddings from purchases/interactions)
- Graph neighborhood (connected products via bipartite graph)
- Budget patterns (price distribution, average spend)
- Style/category preferences

Room Profiles:
- Aggregated product embeddings (mean of products in room)
- Combined color palette
- Style coherence score
- Price range
"""

import json
import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import qdrant_config


class UserProfileIndexer:
    """Build and index user profiles into Qdrant"""
    
    def __init__(self, qdrant_url: str = None, qdrant_api_key: str = None):
        url = qdrant_url or qdrant_config.QDRANT_URL
        api_key = qdrant_api_key or qdrant_config.QDRANT_API_KEY
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = 'users'
    
    def build_user_profile(self,
                          user: Dict,
                          purchases: List[Dict],
                          interactions: List[Dict],
                          product_embeddings: Dict[str, np.ndarray],
                          graph_embeddings: Dict[str, np.ndarray] = None) -> Dict:
        """
        Build a comprehensive user profile.
        
        Args:
            user: User dictionary
            purchases: List of user's purchases
            interactions: List of user's interactions
            product_embeddings: Dict mapping product_id -> CLIP embedding
            graph_embeddings: Dict mapping product_id -> graph embedding
        
        Returns:
            User profile dictionary with embeddings and metadata
        """
        user_id = user['user_id']
        
        # Get user's product interactions
        purchased_product_ids = [p['product_id'] for p in purchases]
        interacted_product_ids = [i['product_id'] for i in interactions]
        all_product_ids = list(set(purchased_product_ids + interacted_product_ids))
        
        # Build preference vector (weighted average of product embeddings)
        preference_embeddings = []
        weights = []
        
        for pid in purchased_product_ids:
            if str(pid) in product_embeddings:
                preference_embeddings.append(product_embeddings[str(pid)])
                weights.append(2.0)  # Purchases weighted higher
        
        for pid in interacted_product_ids:
            if str(pid) in product_embeddings and pid not in purchased_product_ids:
                preference_embeddings.append(product_embeddings[str(pid)])
                weights.append(1.0)
        
        if preference_embeddings:
            weights = np.array(weights)
            preference_vector = np.average(preference_embeddings, axis=0, weights=weights)
        else:
            # Use centroid if available, otherwise zero vector
            preference_vector = np.array(user.get('centroid', np.zeros(512)))
        
        # Build graph neighborhood embedding
        graph_neighborhood = np.zeros(256)
        if graph_embeddings:
            graph_embs = []
            for pid in all_product_ids:
                if str(pid) in graph_embeddings:
                    graph_embs.append(graph_embeddings[str(pid)])
            
            if graph_embs:
                graph_neighborhood = np.mean(graph_embs, axis=0)
        
        # Extract budget patterns
        prices = [p['price_paid'] for p in purchases if 'price_paid' in p]
        budget_stats = {
            'avg_price': np.mean(prices) if prices else 0,
            'min_price': np.min(prices) if prices else 0,
            'max_price': np.max(prices) if prices else 0,
            'total_spent': np.sum(prices) if prices else 0,
            'num_purchases': len(purchases)
        }
        
        # Extract category/style preferences
        categories = defaultdict(int)
        styles = defaultdict(int)
        
        for purchase in purchases:
            if 'category' in purchase:
                categories[purchase['category']] += 1
        
        # Build profile
        profile = {
            'user_id': user_id,
            'preference_vector': preference_vector,
            'graph_neighborhood': graph_neighborhood,
            'budget': budget_stats,
            'favorite_categories': dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]),
            'num_purchases': len(purchases),
            'num_interactions': len(interactions),
            'active_products': all_product_ids[:20]  # Top 20 recent
        }
        
        return profile
    
    def index_users(self, 
                   users: List[Dict],
                   purchases: List[Dict],
                   interactions: List[Dict],
                   product_embeddings: Dict[str, np.ndarray],
                   graph_embeddings: Dict[str, np.ndarray] = None,
                   batch_size: int = 100) -> int:
        """
        Index all users into Qdrant.
        
        Args:
            users: List of user dictionaries
            purchases: List of all purchases
            interactions: List of all interactions
            product_embeddings: Product CLIP embeddings
            graph_embeddings: Product graph embeddings
            batch_size: Batch size for indexing
        
        Returns:
            Number of users indexed
        """
        print(f"\nIndexing {len(users)} users...")
        
        # Group purchases and interactions by user
        user_purchases = defaultdict(list)
        user_interactions = defaultdict(list)
        
        for purchase in purchases:
            user_purchases[purchase['user_id']].append(purchase)
        
        for interaction in interactions:
            user_interactions[interaction['user_id']].append(interaction)
        
        # Build and index profiles
        points = []
        
        for user in tqdm(users, desc="Building user profiles"):
            user_id = user['user_id']
            
            # Build profile
            profile = self.build_user_profile(
                user,
                user_purchases[user_id],
                user_interactions[user_id],
                product_embeddings,
                graph_embeddings
            )
            
            # Create point
            vectors = {
                'preference': profile['preference_vector'].tolist(),
                'graph_neighborhood': profile['graph_neighborhood'].tolist()
            }
            
            payload = {
                'user_id': user_id,
                'budget_avg': profile['budget']['avg_price'],
                'budget_min': profile['budget']['min_price'],
                'budget_max': profile['budget']['max_price'],
                'total_spent': profile['budget']['total_spent'],
                'num_purchases': profile['num_purchases'],
                'num_interactions': profile['num_interactions'],
                'favorite_categories': profile['favorite_categories'],
                'active_products': profile['active_products']
            }
            
            point = PointStruct(
                id=hash(user_id) % (2**31),
                vector=vectors,
                payload=payload
            )
            
            points.append(point)
            
            # Batch upload
            if len(points) >= batch_size:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                points = []
        
        # Upload remaining
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        
        print(f"✓ Indexed {len(users)} users")
        return len(users)


class RoomProfileIndexer:
    """Build and index room profiles into Qdrant"""
    
    def __init__(self, qdrant_url: str = None, qdrant_api_key: str = None):
        url = qdrant_url or qdrant_config.QDRANT_URL
        api_key = qdrant_api_key or qdrant_config.QDRANT_API_KEY
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = 'rooms'
    
    def build_room_profile(self,
                          room_id: str,
                          room_name: str,
                          product_ids: List[str],
                          products: Dict[str, Dict],
                          product_embeddings: Dict[str, np.ndarray],
                          color_features: Dict[str, np.ndarray] = None) -> Dict:
        """
        Build a room profile from constituent products.
        
        Args:
            room_id: Unique room identifier
            room_name: Room name/description
            product_ids: List of product IDs in the room
            products: Dict mapping product_id -> product data
            product_embeddings: Dict mapping product_id -> CLIP embedding
            color_features: Dict mapping product_id -> color vector
        
        Returns:
            Room profile dictionary
        """
        # Aggregate embeddings
        room_embeddings = []
        room_colors = []
        room_products = []
        total_price = 0
        categories = defaultdict(int)
        styles = defaultdict(int)
        
        for pid in product_ids:
            if str(pid) in product_embeddings:
                room_embeddings.append(product_embeddings[str(pid)])
            
            if color_features and str(pid) in color_features:
                room_colors.append(color_features[str(pid)])
            
            if str(pid) in products:
                product = products[str(pid)]
                room_products.append(product)
                total_price += product.get('price', 0)
                
                if 'category' in product:
                    categories[product['category']] += 1
                
                for style in product.get('styles', []):
                    styles[style] += 1
        
        # Aggregate vectors
        if room_embeddings:
            room_profile_vector = np.mean(room_embeddings, axis=0)
        else:
            room_profile_vector = np.zeros(512)
        
        if room_colors:
            room_color_vector = np.mean(room_colors, axis=0)
        else:
            room_color_vector = np.zeros(548)
        
        # Calculate style coherence (how uniform are the styles)
        style_coherence = 0.0
        if styles:
            max_style_count = max(styles.values())
            style_coherence = max_style_count / sum(styles.values())
        
        profile = {
            'room_id': room_id,
            'room_name': room_name,
            'room_profile': room_profile_vector,
            'color_palette': room_color_vector,
            'num_products': len(product_ids),
            'total_price': total_price,
            'avg_price': total_price / len(product_ids) if product_ids else 0,
            'categories': dict(categories),
            'styles': dict(styles),
            'dominant_style': max(styles.items(), key=lambda x: x[1])[0] if styles else None,
            'style_coherence': style_coherence,
            'product_ids': product_ids
        }
        
        return profile
    
    def index_rooms(self,
                   rooms: List[Dict],
                   products: Dict[str, Dict],
                   product_embeddings: Dict[str, np.ndarray],
                   color_features: Dict[str, np.ndarray] = None,
                   batch_size: int = 50) -> int:
        """
        Index room profiles into Qdrant.
        
        Args:
            rooms: List of room dictionaries with 'room_id', 'name', 'products'
            products: Dict of all products
            product_embeddings: Product CLIP embeddings
            color_features: Product color features
            batch_size: Batch size for indexing
        
        Returns:
            Number of rooms indexed
        """
        print(f"\nIndexing {len(rooms)} rooms...")
        
        points = []
        
        for room in tqdm(rooms, desc="Building room profiles"):
            profile = self.build_room_profile(
                room['room_id'],
                room['name'],
                room['products'],
                products,
                product_embeddings,
                color_features
            )
            
            vectors = {
                'room_profile': profile['room_profile'].tolist(),
                'color_palette': profile['color_palette'].tolist()
            }
            
            payload = {
                'room_id': profile['room_id'],
                'room_name': profile['room_name'],
                'num_products': profile['num_products'],
                'total_price': profile['total_price'],
                'avg_price': profile['avg_price'],
                'categories': profile['categories'],
                'styles': profile['styles'],
                'dominant_style': profile['dominant_style'],
                'style_coherence': profile['style_coherence'],
                'product_ids': profile['product_ids']
            }
            
            point = PointStruct(
                id=hash(room['room_id']) % (2**31),
                vector=vectors,
                payload=payload
            )
            
            points.append(point)
            
            if len(points) >= batch_size:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                points = []
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        
        print(f"✓ Indexed {len(rooms)} rooms")
        return len(rooms)


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Index user and room profiles"""
    
    print("="*80)
    print("FURNIVERSE USER & ROOM PROFILE INDEXER")
    print("="*80)
    
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'Data' / 'processed'
    
    # Load data
    print("\nLoading data...")
    with open(data_dir / 'users.json', 'r') as f:
        users = json.load(f)
    with open(data_dir / 'purchases.json', 'r') as f:
        purchases = json.load(f)
    with open(data_dir / 'interactions.json', 'r') as f:
        interactions = json.load(f)
    with open(data_dir / 'products.json', 'r') as f:
        products_list = json.load(f)
    
    products = {str(p['id']): p for p in products_list}
    
    print(f"✓ Loaded {len(users)} users, {len(purchases)} purchases, {len(interactions)} interactions")
    
    # Load embeddings from Qdrant or generate dummy ones
    print("\nNote: Using user centroids as preference vectors")
    print("For production, load CLIP embeddings from Qdrant products collection")
    
    product_embeddings = {}
    for user in users[:len(products_list)]:
        if 'centroid' in user:
            # Map user centroids to products for demo
            idx = users.index(user)
            if idx < len(products_list):
                product_embeddings[str(products_list[idx]['id'])] = np.array(user['centroid'])
    
    # Index users
    user_indexer = UserProfileIndexer()
    user_indexer.index_users(
        users[:100],  # Index first 100 users for demo
        purchases,
        interactions,
        product_embeddings
    )
    
    # Create sample rooms for demo
    print("\nCreating sample room profiles...")
    sample_rooms = [
        {
            'room_id': 'room_living_modern',
            'name': 'Modern Living Room',
            'products': [str(p['id']) for p in products_list[:5] if p.get('category') == 'Three-seat sofas'][:3]
        },
        {
            'room_id': 'room_bedroom_cozy',
            'name': 'Cozy Bedroom',
            'products': [str(p['id']) for p in products_list if 'bed' in p.get('category', '').lower()][:4]
        }
    ]
    
    # Index rooms
    room_indexer = RoomProfileIndexer()
    room_indexer.index_rooms(
        sample_rooms,
        products,
        product_embeddings
    )
    
    print("\n" + "="*80)
    print("✓ PROFILE INDEXING COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()

"""
Semantic Synthetic Data Generator for Furniverse Recommendation Engine

Orchestrates the generation of users, purchases, and interactions based on
product embeddings to ensure semantically coherent patterns.

Scale: 1K users, 3K purchases, 20K interactions (403 products)

Output:
    - Data/processed/users.json
    - Data/processed/purchases.json  
    - Data/processed/interactions.json
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

# Add Pipeline to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from embeddings.engine import EmbeddingEngine
from synthetic.generate_users import generate_user_centroids
from synthetic.generate_purchases import generate_purchases
from synthetic.generate_interactions import generate_interactions


# ============================================================================
# CONFIGURATION
# ============================================================================

NUM_USERS = 1000
NUM_PURCHASES = 3000
NUM_INTERACTIONS = 20000


# ============================================================================
# DATA LOADING
# ============================================================================

def load_products() -> List[Dict[str, Any]]:
    """Load products from raw data"""
    project_root = Path(__file__).parent.parent.parent
    products_path = project_root / 'Data' / 'raw' / 'products.json'
    
    with open(products_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"✓ Loaded {len(products)} products")
    return products


def embed_products(products: List[Dict], engine: EmbeddingEngine) -> np.ndarray:
    """Generate text embeddings for all products using EmbeddingEngine"""
    print("\nEmbedding products with SBERT (via EmbeddingEngine)...")
    
    # Create rich text representation
    texts = []
    for p in products:
        text = f"{p['name']} {p['description']} {' '.join(p.get('styles', []))} {p['category']}"
        texts.append(text)
    
    # Use the centralized embedding engine
    embeddings = engine.sbert.encode(texts, show_progress_bar=True)
    print(f"✓ Generated embeddings: {embeddings.shape}")
    
    return embeddings


# ============================================================================
# OUTPUT
# ============================================================================

def save_output(users: List[Dict], purchases: List[Dict], interactions: List[Dict]):
    """Save generated data to Data/processed/"""
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / 'Data' / 'processed'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files = {
        'users.json': users,
        'purchases.json': purchases,
        'interactions.json': interactions
    }
    
    print("\nSaving outputs...")
    for filename, data in files.items():
        path = output_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ {path} ({len(data)} records)")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*80)
    print("FURNIVERSE SYNTHETIC DATA GENERATOR")
    print("="*80)
    
    # Initialize embedding engine (Qdrant)
    engine = EmbeddingEngine(
        qdrant_host='localhost',
        qdrant_port=6333,
        collection_name='furniture_products'
    )
    
    # Load data
    products = load_products()
    
    # Generate embeddings
    embeddings = embed_products(products, engine)
    
    # Generate synthetic data using vector centroids
    users = generate_user_centroids(products, embeddings, NUM_USERS)
    purchases = generate_purchases(users, products, embeddings, NUM_PURCHASES)
    interactions = generate_interactions(users, products, purchases, embeddings, NUM_INTERACTIONS)
    
    # Save outputs
    save_output(users, purchases, interactions)
    
    print("\n" + "="*80)
    print("✓ GENERATION COMPLETE")
    print("="*80)
    print(f"  Users: {len(users)}")
    print(f"  Purchases: {len(purchases)}")
    print(f"  Interactions: {len(interactions)}")
    print(f"  Products: {len(products)}")


if __name__ == '__main__':
    main()

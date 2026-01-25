"""
Qdrant Product Indexing Pipeline for Furniverse

Complete indexing pipeline that combines:
1. CLIP embeddings (text + image) for multimodal search
2. Color palette features (RGB + HSV) for color-based filtering
3. Node2Vec graph embeddings for relationship-based recommendations

This creates a rich, multimodal vector database in Qdrant that enables:
- Semantic search across text and images
- Color-based product discovery
- Graph-based substitute recommendations
- Budget-aware filtering
"""

import json
import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from embeddings.engine import EmbeddingEngine
from embeddings.color_extractor import ColorExtractor, extract_product_color_features
from graph.build_graph import ProductGraphBuilder
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, NamedVector
import qdrant_config


class MultimodalIndexer:
    """
    Indexes products into Qdrant with multimodal features:
    - CLIP text embeddings (512d)
    - CLIP image embeddings (512d)
    - Color features (RGB + HSV)
    - Graph embeddings (256d from Node2Vec)
    """
    
    def __init__(self, 
                 qdrant_url: str = None,
                 qdrant_api_key: str = None,
                 use_clip: bool = True,
                 use_colors: bool = True,
                 use_graph: bool = True):
        """
        Initialize the multimodal indexer.
        
        Args:
            qdrant_url: Qdrant Cloud URL (uses config if None)
            qdrant_api_key: Qdrant Cloud API key (uses config if None)
            use_clip: Whether to generate CLIP embeddings
            use_colors: Whether to extract color features
            use_graph: Whether to compute graph embeddings
        """
        self.qdrant_url = qdrant_url or qdrant_config.QDRANT_URL
        self.qdrant_api_key = qdrant_api_key or qdrant_config.QDRANT_API_KEY
        self.use_clip = use_clip
        self.use_colors = use_colors
        self.use_graph = use_graph
        
        # Initialize components
        self.client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
        self.embedding_engine = EmbeddingEngine(
            qdrant_url=self.qdrant_url,
            qdrant_api_key=self.qdrant_api_key
        )
        self.color_extractor = ColorExtractor(n_colors=5) if use_colors else None
        self.graph_builder = ProductGraphBuilder() if use_graph else None
        
        print(f"✓ Connected to Qdrant Cloud")
    
    def create_collections(self):
        """Create Qdrant collections with named vectors for multimodal search"""
        
        collections = {
            'products_multimodal': {
                'text_clip': 512,      # CLIP text embeddings
                'image_clip': 512,     # CLIP image embeddings
                'color': 548,          # Color features (5*6 + 6 + 512 histogram)
                'graph': 256           # Node2Vec graph embeddings
            },
            'users': {
                'preference': 512,     # User preference vector (CLIP-based)
                'graph_neighborhood': 256  # User's graph neighborhood
            },
            'rooms': {
                'room_profile': 512,   # Aggregated room embedding
                'color_palette': 548   # Aggregated room colors
            }
        }
        
        for collection_name, vectors_config in collections.items():
            try:
                # Check if collection exists
                self.client.get_collection(collection_name)
                print(f"✓ Collection '{collection_name}' already exists")
            except:
                # Create collection with named vectors
                named_vectors = {
                    name: VectorParams(size=dim, distance=Distance.COSINE)
                    for name, dim in vectors_config.items()
                }
                
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=named_vectors
                )
                print(f"✓ Created collection '{collection_name}' with {len(named_vectors)} vector types")
    
    def index_products(self, products: List[Dict], batch_size: int = 50) -> int:
        """
        Index products into Qdrant with all multimodal features.
        
        Args:
            products: List of product dictionaries
            batch_size: Batch size for indexing
        
        Returns:
            Number of products indexed
        """
        print(f"\nIndexing {len(products)} products into Qdrant...")
        print("="*80)
        
        # Step 1: Build graph and compute graph embeddings
        graph_embeddings = {}
        if self.use_graph:
            print("\n[1/4] Building product graph and computing Node2Vec embeddings...")
            
            # Create simple text embeddings for graph building
            text_embs = []
            print("  - Generating text embeddings for graph...")
            for product in tqdm(products, desc="  Text embeddings"):
                text = f"{product['name']} {product['description']} {product.get('category', '')}"
                emb = self.embedding_engine.sbert.encode(text)
                text_embs.append(emb)
            
            text_embs = np.array(text_embs)
            
            # Build graph
            self.graph_builder.build_similarity_graph(products, text_embs, k_neighbors=10)
            self.graph_builder.build_category_graph(products)
            self.graph_builder.build_combined_graph()
            
            # Compute Node2Vec embeddings
            graph_embeddings = self.graph_builder.compute_node2vec_embeddings(
                dimensions=256,
                walk_length=30,
                num_walks=200
            )
            
            print(f"  ✓ Graph embeddings computed for {len(graph_embeddings)} products")
        
        # Step 2: Generate CLIP embeddings
        clip_text_embs = {}
        clip_image_embs = {}
        
        if self.use_clip:
            print("\n[2/4] Generating CLIP embeddings...")
            
            for product in tqdm(products, desc="  CLIP embeddings"):
                pid = str(product['id'])
                
                # Text embedding
                text = f"{product['name']}. {product['description']}"
                try:
                    clip_text_embs[pid] = self.embedding_engine.clip.encode_text(text)[0]
                except Exception as e:
                    print(f"  ⚠ Failed CLIP text for {pid}: {e}")
                    clip_text_embs[pid] = np.zeros(512, dtype=np.float32)
                
                # Image embedding
                image_url = product.get('primary_image') or product.get('image')
                if image_url:
                    try:
                        clip_image_embs[pid] = self.embedding_engine.clip.encode_image(image_url)
                    except Exception as e:
                        print(f"  ⚠ Failed CLIP image for {pid}: {e}")
                        clip_image_embs[pid] = np.zeros(512, dtype=np.float32)
                else:
                    clip_image_embs[pid] = np.zeros(512, dtype=np.float32)
            
            print(f"  ✓ Generated CLIP embeddings for {len(clip_text_embs)} products")
        
        # Step 3: Extract color features
        color_features = {}
        
        if self.use_colors:
            print("\n[3/4] Extracting color features...")
            
            for product in tqdm(products, desc="  Color extraction"):
                pid = str(product['id'])
                
                try:
                    features = extract_product_color_features(product, self.color_extractor)
                    color_features[pid] = features['color_vector']
                except Exception as e:
                    print(f"  ⚠ Failed color extraction for {pid}: {e}")
                    # Fallback: zero vector
                    color_features[pid] = np.zeros(548, dtype=np.float32)
            
            print(f"  ✓ Extracted colors for {len(color_features)} products")
        
        # Step 4: Index into Qdrant (with batching to avoid timeouts)
        print("\n[4/4] Uploading to Qdrant...")
        
        batch_size = 20  # Upload 20 products at a time
        points = []
        for product in tqdm(products, desc="  Building points"):
            pid = str(product['id'])
            product_id_int = int(product['id']) if str(product['id']).isdigit() else hash(str(product['id'])) % (2**31)
            
            # Build named vectors
            vectors = {}
            
            if self.use_clip and pid in clip_text_embs:
                vectors['text_clip'] = clip_text_embs[pid].tolist()
                vectors['image_clip'] = clip_image_embs[pid].tolist()
            
            if self.use_colors and pid in color_features:
                vectors['color'] = color_features[pid].tolist()
            
            if self.use_graph and pid in graph_embeddings:
                vectors['graph'] = graph_embeddings[pid].tolist()
            
            # Build payload
            payload = {
                'product_id': pid,
                'name': product.get('name'),
                'category': product.get('category'),
                'price': product.get('price'),
                'rating': product.get('rating'),
                'review_count': product.get('reviewCount'),
                'description': product.get('description', '')[:500],  # Truncate
                'styles': product.get('styles', []),
                'colors': product.get('colors', []),
                'tags': product.get('tags', []),
                'in_stock': product.get('inStock', True),
                'image': product.get('image'),
                'primary_image': product.get('primary_image')
            }
            
            # Add color palette to payload
            if self.use_colors and pid in color_features:
                try:
                    palette = self.color_extractor.get_color_palette_dict(
                        product.get('primary_image') or product.get('image')
                    )
                    payload['color_palette'] = palette
                except:
                    pass
            
            point = PointStruct(
                id=product_id_int,
                vector=vectors,
                payload=payload
            )
            
            points.append(point)
            
            # Batch upload
            if len(points) >= batch_size:
                self.client.upsert(
                    collection_name='products_multimodal',
                    points=points
                )
                print(f"    \u2713 Uploaded batch ({len(points)} products)")
                points = []
        
        # Upload remaining points
        if points:
            self.client.upsert(
                collection_name='products_multimodal',
                points=points
            )
            print(f"    \u2713 Uploaded final batch ({len(points)} products)")
        
        print(f"  ✓ Indexed {len(products)} products into Qdrant")
        
        return len(products)
    
    def verify_indexing(self, collection_name: str = 'products_multimodal'):
        """
        Verify that indexing was successful.
        
        Args:
            collection_name: Name of collection to verify
        """
        print(f"\nVerifying collection '{collection_name}'...")
        
        try:
            info = self.client.get_collection(collection_name)
            print(f"  ✓ Collection exists")
            print(f"  - Points count: {info.points_count}")
            print(f"  - Vectors count: {info.vectors_count}")
            print(f"  - Status: {info.status}")
            
            # Test search
            print(f"\n  Testing search...")
            test_vector = np.random.randn(512).tolist()
            results = self.client.search(
                collection_name=collection_name,
                query_vector=('text_clip', test_vector),
                limit=3
            )
            print(f"  ✓ Search working - got {len(results)} results")
            
            if results:
                print(f"  - Sample result: {results[0].payload.get('name')}")
            
        except Exception as e:
            print(f"  ✗ Verification failed: {e}")
    
    def get_collection_stats(self):
        """Print statistics for all collections"""
        print("\nQdrant Collection Statistics:")
        print("="*80)
        
        collections = ['products_multimodal', 'users', 'rooms']
        
        for collection_name in collections:
            try:
                info = self.client.get_collection(collection_name)
                print(f"\n{collection_name}:")
                print(f"  Points: {info.points_count}")
                print(f"  Vectors: {info.vectors_count}")
                print(f"  Status: {info.status}")
            except:
                print(f"\n{collection_name}: Not found")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main indexing pipeline"""
    
    print("="*80)
    print("FURNIVERSE MULTIMODAL INDEXING PIPELINE")
    print("="*80)
    print("\nThis pipeline will:")
    print("  1. Build product similarity graph")
    print("  2. Compute Node2Vec graph embeddings")
    print("  3. Generate CLIP text + image embeddings")
    print("  4. Extract color palette features (RGB + HSV)")
    print("  5. Index everything into Qdrant")
    print("="*80)
    
    # Load products
    project_root = Path(__file__).parent.parent.parent
    products_path = project_root / 'Data' / 'processed' / 'products.json'
    
    print(f"\nLoading products from {products_path}...")
    with open(products_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"✓ Loaded {len(products)} products")
    
    # Initialize indexer
    print("\nInitializing indexer...")
    indexer = MultimodalIndexer(
        use_clip=True,
        use_colors=True,
        use_graph=True
    )
    
    # Create collections
    print("\nCreating Qdrant collections...")
    indexer.create_collections()
    
    # Index products (use a subset for testing if too many)
    # For hackathon demo, you might want to limit to first 100-200 products
    products_to_index = products[:200]  # Adjust as needed
    print(f"\n⚠ Indexing first {len(products_to_index)} products (adjust in code if needed)")
    
    indexed_count = indexer.index_products(products_to_index)
    
    # Verify
    print("\n" + "="*80)
    indexer.verify_indexing()
    indexer.get_collection_stats()
    
    print("\n" + "="*80)
    print("✓ INDEXING COMPLETE!")
    print("="*80)
    print(f"\nYou can now:")
    print(f"  - Search products by text: CLIP text embeddings")
    print(f"  - Search by image similarity: CLIP image embeddings")
    print(f"  - Filter by color: Color palette features")
    print(f"  - Find substitutes: Graph embeddings")
    print(f"\nNext steps:")
    print(f"  - Run Backend API with recommendation endpoints")
    print(f"  - Index user profiles")
    print(f"  - Index room profiles")


if __name__ == '__main__':
    main()

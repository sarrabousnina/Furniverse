"""
Persistent storage for embeddings in Qdrant vector database.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


class EmbeddingStorage:
    """
    Handles saving/loading embeddings to/from Qdrant vector database.
    
    Collections:
        - furniture_products: Product embeddings (text + image + graph)
        - user_rooms: User room profile embeddings
    
    Each point stores:
        - id: product_id or user_id
        - vector: Combined embedding
        - payload: metadata (name, category, price, etc.)
    """
    
    def __init__(self, 
                 url: str = None,
                 api_key: str = None,
                 host: str = 'localhost', 
                 port: int = 6333,
                 collection_name: str = 'furniture_products'):
        """
        Initialize Qdrant storage.
        
        Args:
            url: Qdrant Cloud URL (optional)
            api_key: Qdrant Cloud API key (optional)
            host: Qdrant server host (for local)
            port: Qdrant server port (for local)
            collection_name: Name of the collection to use
        """
        if url and api_key:
            self.client = QdrantClient(url=url, api_key=api_key)
        else:
            self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self._cache = {}
    
    def save(self, embeddings: Dict[Any, Dict[str, np.ndarray]], 
             products: Optional[List[Dict]] = None,
             vector_field: str = 'text'):
        """
        Save embeddings to Qdrant.
        
        Args:
            embeddings: Dict mapping product_id -> {'text': array, 'image': array, ...}
            products: Optional list of product metadata dicts
            vector_field: Which embedding to use as primary vector ('text', 'image', or 'combined')
        """
        if not embeddings:
            print("⚠ No embeddings to save")
            return
        
        # Get vector dimension from first embedding
        first_emb = next(iter(embeddings.values()))
        vector_dim = first_emb[vector_field].shape[0]
        
        # Create collection if it doesn't exist
        try:
            self.client.get_collection(self.collection_name)
            print(f"✓ Collection '{self.collection_name}' exists")
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE)
            )
            print(f"✓ Created collection '{self.collection_name}' with dim={vector_dim}")
        
        # Prepare points
        points = []
        product_map = {str(p['id']): p for p in products} if products else {}
        
        for product_id, emb_dict in embeddings.items():
            # Use specified vector field
            vector = emb_dict[vector_field].tolist()
            
            # Build payload with metadata
            payload = {
                'embedding_types': list(emb_dict.keys()),
                'saved_at': datetime.now().isoformat()
            }
            
            # Add product metadata if available
            if str(product_id) in product_map:
                product = product_map[str(product_id)]
                payload.update({
                    'name': product.get('name'),
                    'category': product.get('category'),
                    'price': product.get('price'),
                    'rating': product.get('rating'),
                    'styles': product.get('styles', []),
                    'colors': product.get('colors', []),
                    'in_stock': product.get('inStock', True),
                    'image': product.get('image')
                })
            
            points.append(PointStruct(
                id=int(product_id) if str(product_id).isdigit() else hash(str(product_id)) % (2**31),
                vector=vector,
                payload=payload
            ))
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        # Update cache
        self._cache = embeddings
        
        print(f"✓ Saved {len(points)} embeddings to Qdrant collection '{self.collection_name}'")
    
    def load(self) -> Dict[Any, Dict[str, np.ndarray]]:
        """
        Load embeddings from Qdrant.
        
        Returns:
            Dict mapping product_id -> {'vector': array, 'payload': dict}
            
        Note: This loads vectors but not the full multimodal embeddings.
        Use get_by_id() for full embedding retrieval.
        """
        # Return cached version if available
        if self._cache:
            return self._cache
        
        try:
            # Scroll through all points
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000,
                with_payload=True,
                with_vectors=True
            )
            
            embeddings = {}
            for point in points:
                embeddings[point.id] = {
                    'vector': np.array(point.vector),
                    'payload': point.payload
                }
            
            self._cache = embeddings
            
            print(f"✓ Loaded {len(embeddings)} embeddings from Qdrant")
            return embeddings
            
        except Exception as e:
            print(f"⚠ Failed to load from Qdrant: {e}")
            return {}
    
    def get_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single product embedding by ID"""
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[product_id],
                with_payload=True,
                with_vectors=True
            )
            if points:
                return {
                    'vector': np.array(points[0].vector),
                    'payload': points[0].payload
                }
        except Exception as e:
            print(f"⚠ Error retrieving ID {product_id}: {e}")
        return None
    
    def search(self, query_vector: np.ndarray, limit: int = 10, 
               filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar embeddings.
        
        Args:
            query_vector: Query embedding vector
            limit: Number of results
            filter_dict: Qdrant filter conditions
        
        Returns:
            List of {id, score, payload} dicts
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit,
            query_filter=filter_dict
        )
        
        return [
            {
                'id': r.id,
                'score': r.score,
                'payload': r.payload
            }
            for r in results
        ]
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get metadata about the collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': self.collection_name,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            return {'error': str(e)}
    
    def exists(self) -> bool:
        """Check if collection exists in Qdrant"""
        try:
            self.client.get_collection(self.collection_name)
            return True
        except:
            return False
    
    def clear_cache(self):
        """Clear in-memory cache"""
        self._cache = {}
    
    def delete_collection(self):
        """Delete the entire collection (use with caution!)"""
        self.client.delete_collection(self.collection_name)
        self._cache = {}
        print(f"✓ Deleted collection '{self.collection_name}'")
    
    def __repr__(self):
        exists = "exists" if self.exists() else "not found"
        return f"EmbeddingStorage(collection='{self.collection_name}', {exists})"

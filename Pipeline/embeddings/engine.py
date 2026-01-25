from .models import SBERTModel, CLIPModel, GraphModel
from .storage import EmbeddingStorage
import numpy as np

class EmbeddingEngine:
    """Single source of truth for all embeddings"""
    
    def __init__(self, 
                 qdrant_url: str = None,
                 qdrant_api_key: str = None,
                 qdrant_host: str = 'localhost',
                 qdrant_port: int = 6333,
                 collection_name: str = 'furniture_products'):
        self.sbert = SBERTModel()
        self.clip = CLIPModel()
        self.graph = GraphModel()
        
        # Support both cloud and local connections
        if qdrant_url and qdrant_api_key:
            from qdrant_client import QdrantClient
            self.storage = EmbeddingStorage(
                url=qdrant_url,
                api_key=qdrant_api_key,
                collection_name=collection_name
            )
        else:
            self.storage = EmbeddingStorage(
                host=qdrant_host,
                port=qdrant_port,
                collection_name=collection_name
            )
    
    # === EMBEDDING METHODS ===
    
    def embed_product_text(self, product):
        """Text embedding for product"""
        text = f"{product['name']} {product['description']} {' '.join(product.get('styles', []))}"
        return self.sbert.encode(text)
    
    def embed_product_image(self, image_url_or_array):
        """Image embedding for product"""
        return self.clip.encode_image(image_url_or_array)
    
    def embed_product_graph(self, product_id, graph):
        """Graph embedding for product"""
        return self.graph.encode_node(product_id, graph)
    
    def embed_user_profile(self, purchased_product_ids):
        """User profile from purchases"""
        embeddings = self.storage.load()
        user_embs = [embeddings[pid]['text'] for pid in purchased_product_ids]
        return np.mean(user_embs, axis=0)
    
    # === BATCH OPERATIONS ===
    
    def batch_embed_products(self, products, vector_field='text'):
        """Embed all products at once and save to Qdrant"""
        embeddings = {}
        for p in products:
            embeddings[p['id']] = {
                'text': self.embed_product_text(p),
                'image': self.embed_product_image(p['image']),
                # 'graph' added later
            }
        self.storage.save(embeddings, products=products, vector_field=vector_field)
        return embeddings
    
    def add_graph_embeddings(self, graph, vector_field='text'):
        """Add graph embeddings to existing"""
        embeddings = self.storage.load()
        for product_id in embeddings.keys():
            embeddings[product_id]['graph'] = self.embed_product_graph(product_id, graph)
        self.storage.save(embeddings, vector_field=vector_field)
    
    # === CONVENIENCE ===
    
    def get_embedding(self, product_id, emb_type='vector'):
        """Get cached embedding from Qdrant"""
        result = self.storage.get_by_id(product_id)
        if result:
            return result.get(emb_type)
        return None
    
    def search_similar(self, query_vector, limit=10, filter_dict=None):
        """Search for similar products in Qdrant"""
        return self.storage.search(query_vector, limit, filter_dict)
    
    def get_all_embeddings(self):
        """Get all cached embeddings from Qdrant"""
        return self.storage.load()
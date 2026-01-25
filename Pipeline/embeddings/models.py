"""
Embedding models for text, images, and graph structures.
All models are lazy-loaded to avoid unnecessary initialization.
"""

import numpy as np
from typing import Union, List
import warnings


class SBERTModel:
    """Sentence Transformers text encoder"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        self.model_name = model_name
        self._model = None
    
    @property
    def model(self):
        """Lazy load the model"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            print(f"Loading SentenceTransformer model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def encode(self, text: Union[str, List[str]], **kwargs) -> np.ndarray:
        """
        Encode text to embeddings.
        
        Args:
            text: Single string or list of strings
            **kwargs: Additional arguments (show_progress_bar supported)
        
        Returns:
            numpy array of shape (dim,) for single text or (n, dim) for list
        """
        # Convert single string to list
        is_single = isinstance(text, str)
        if is_single:
            text = [text]
        
        # Encode using sentence-transformers
        embeddings = self.model.encode(text, **kwargs)
        
        # Return single embedding or batch
        return embeddings[0] if is_single else embeddings
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return 384  # all-MiniLM-L6-v2 dimension


class CLIPModel:
    """CLIP multimodal encoder (text + images)"""
    
    def __init__(self, model_name: str = 'openai/clip-vit-base-patch32'):
        self.model_name = model_name
        self._model = None
        self._processor = None
    
    @property
    def model(self):
        """Lazy load the model"""
        if self._model is None:
            try:
                from transformers import CLIPModel as HFCLIPModel, CLIPProcessor
                print(f"Loading CLIP model: {self.model_name}...")
                self._model = HFCLIPModel.from_pretrained(self.model_name)
                self._processor = CLIPProcessor.from_pretrained(self.model_name)
            except ImportError:
                warnings.warn("transformers not installed. CLIP features disabled.")
                raise
        return self._model
    
    @property
    def processor(self):
        """Lazy load the processor (loads model first if needed)"""
        if self._processor is None:
            _ = self.model  # Trigger model loading which also loads processor
        return self._processor
    
    def encode_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Encode text with CLIP text encoder"""
        if isinstance(text, str):
            text = [text]
        
        # Truncate to max 77 tokens (CLIP's limit)
        inputs = self.processor(text=text, return_tensors="pt", padding=True, truncation=True, max_length=77)
        outputs = self.model.get_text_features(**inputs)
        
        return outputs.detach().numpy()
    
    def encode_image(self, image_url_or_array) -> np.ndarray:
        """
        Encode image with CLIP image encoder.
        
        Args:
            image_url_or_array: URL string, PIL Image, or numpy array
        
        Returns:
            numpy array of shape (512,)
        """
        from PIL import Image
        import requests
        from io import BytesIO
        from pathlib import Path
        
        # Load image
        if isinstance(image_url_or_array, str):
            if image_url_or_array.startswith('http'):
                response = requests.get(image_url_or_array, timeout=10)
                image = Image.open(BytesIO(response.content)).convert('RGB')
            elif image_url_or_array.startswith('/'):
                # Handle local paths starting with /
                project_root = Path(__file__).parent.parent.parent
                image_path = image_url_or_array.lstrip('/')
                if image_path.startswith('images/products/'):
                    image_path = image_path[len('images/products/'):]
                full_path = project_root / 'Data' / 'raw' / 'images' / image_path
                image = Image.open(full_path).convert('RGB')
            else:
                image = Image.open(image_url_or_array).convert('RGB')
        else:
            image = image_url_or_array
        
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model.get_image_features(**inputs)
        
        return outputs.detach().numpy().squeeze()
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return 512  # CLIP standard dimension


class GraphModel:
    """Graph structure encoder (Node2Vec/Graph2Vec)"""
    
    def __init__(self):
        self._embeddings = {}
    
    def encode_node(self, node_id: Union[str, int], graph) -> np.ndarray:
        """
        Encode a node in a graph.
        
        Args:
            node_id: Node identifier
            graph: NetworkX graph object
        
        Returns:
            numpy array of node embedding
        """
        # Check if we have pre-computed embeddings
        if node_id in self._embeddings:
            return self._embeddings[node_id]
        
        # If not, compute on-the-fly using Node2Vec
        try:
            from node2vec import Node2Vec
            import networkx as nx
            
            if not isinstance(graph, nx.Graph):
                raise ValueError("Graph must be a NetworkX graph")
            
            # Run Node2Vec
            node2vec = Node2Vec(graph, dimensions=256, walk_length=30, 
                               num_walks=200, workers=4, quiet=True)
            model = node2vec.fit(window=10, min_count=1)
            
            # Cache all embeddings
            for node in graph.nodes():
                self._embeddings[node] = model.wv[str(node)]
            
            return self._embeddings[node_id]
            
        except ImportError:
            warnings.warn("node2vec not installed. Using fallback embeddings.")
            # Fallback: random embeddings (for testing only)
            return np.random.randn(256).astype(np.float32)
    
    def encode_graph(self, graph) -> dict:
        """
        Encode all nodes in a graph.
        
        Args:
            graph: NetworkX graph object
        
        Returns:
            dict mapping node_id -> embedding
        """
        embeddings = {}
        for node in graph.nodes():
            embeddings[node] = self.encode_node(node, graph)
        return embeddings
    
    def set_embeddings(self, embeddings: dict):
        """
        Manually set pre-computed graph embeddings.
        
        Args:
            embeddings: dict mapping node_id -> numpy array
        """
        self._embeddings = embeddings
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return 256

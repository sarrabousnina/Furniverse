"""
Embedding models for text, images, and graph structures.
All models are lazy-loaded to avoid unnecessary initialization.
"""

import numpy as np
from typing import Union, List
import warnings


class SBERTModel:
    """FastEmbed text encoder (lightweight ONNX-based)"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        self.model_name = model_name
        self._model = None
    
    @property
    def model(self):
        """Lazy load the model"""
        if self._model is None:
            from fastembed import TextEmbedding
            print(f"Loading FastEmbed model: {self.model_name}...")
            self._model = TextEmbedding(model_name=self.model_name)
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
        
        # FastEmbed returns generator, convert to numpy array
        embeddings = list(self.model.embed(text))
        result = np.array(embeddings)
        
        # Return single embedding or batch
        return result[0] if is_single else result
    
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
    
    def encode_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Encode text with CLIP text encoder"""
        if isinstance(text, str):
            text = [text]
        
        inputs = self._processor(text=text, return_tensors="pt", padding=True)
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
        
        # Load image
        if isinstance(image_url_or_array, str):
            if image_url_or_array.startswith('http'):
                response = requests.get(image_url_or_array, timeout=10)
                image = Image.open(BytesIO(response.content)).convert('RGB')
            else:
                image = Image.open(image_url_or_array).convert('RGB')
        else:
            image = image_url_or_array
        
        inputs = self._processor(images=image, return_tensors="pt")
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

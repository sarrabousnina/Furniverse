"""
Trade-off Helper Functions
Business logic for preference extraction and trade-off calculations
"""
from typing import Optional
import numpy as np
from services import embedding_tradeoff


def extract_user_preferences(query: str, query_embedding: Optional[np.ndarray], clip_model, clip_processor) -> dict:
    """
    Extract user preferences from natural language query using CLIP embeddings

    Args:
        query: User's natural language query
        query_embedding: Pre-computed CLIP embedding (optional, will compute if not provided)
        clip_model: CLIP model instance
        clip_processor: CLIP processor instance

    Returns:
        dict with keys: budget, material, style, color, comfort, confidences
    """
    # If no embedding provided, compute it
    if query_embedding is None:
        inputs = clip_processor(text=[query], return_tensors="pt", padding=True, truncation=True)
        text_features = clip_model.get_text_features(**inputs)
        query_embedding = text_features.detach().numpy()[0]

    # Use embedding-based extractor
    if embedding_tradeoff.attribute_extractor is not None:
        return embedding_tradeoff.attribute_extractor.extract_preferences(query, query_embedding)
    else:
        # Fallback to simple extraction if not initialized
        print("⚠️ Embedding extractor not initialized, using fallback")
        return {
            "budget": None,
            "material": None,
            "style": None,
            "color": None,
            "comfort": None,
            "confidences": {}
        }


def calculate_tradeoffs(product: dict, preferences: dict, query_embedding: Optional[np.ndarray] = None) -> dict:
    """
    Calculate trade-offs between product and user preferences using CLIP embeddings

    Args:
        product: Product data
        preferences: Extracted user preferences
        query_embedding: CLIP embedding of user query (optional)

    Returns:
        dict with gains, loses, score, is_compromise, similarity, match_explanation
    """
    if embedding_tradeoff.tradeoff_analyzer is not None and query_embedding is not None:
        # Use embedding-based analyzer
        return embedding_tradeoff.tradeoff_analyzer.analyze_tradeoffs(product, preferences, query_embedding)
    else:
        # Fallback to simple analysis
        if query_embedding is None:
            print("⚠️ No query embedding provided for trade-off analysis")
        if embedding_tradeoff.tradeoff_analyzer is None:
            print("⚠️ Trade-off analyzer not initialized")

        return {
            "gains": ["✓ Product found"],
            "loses": [],
            "score": 1,
            "is_compromise": False,
            "similarity": 0.0,
            "match_explanation": "Basic match (embedding analysis unavailable)"
        }

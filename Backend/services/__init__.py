"""
Backend Services Module
Contains core business logic and service classes
"""

from .room_analysis import RoomAnalyzer
from .product_comparison import ProductComparator
from .embedding_tradeoff import EmbeddingAttributeExtractor, EmbeddingTradeoffAnalyzer
from .tripo_generator import TripoGenerator
from .user_activity import tracker, UserEvent
from .models import (
    Dimensions,
    ColorVariant,
    Product,
    RecommendRequest,
    ProductRecommendation,
    TradeOffSearchRequest
)
from .repository import ProductRepository, CSVProductRepository, CATEGORY_MAP

__all__ = [
    'RoomAnalyzer',
    'ProductComparator',
    'EmbeddingAttributeExtractor',
    'EmbeddingTradeoffAnalyzer',
    'TripoGenerator',
    'tracker',
    'UserEvent',
    'Dimensions',
    'ColorVariant',
    'Product',
    'RecommendRequest',
    'ProductRecommendation',
    'TradeOffSearchRequest',
    'ProductRepository',
    'CSVProductRepository',
    'CATEGORY_MAP',
]

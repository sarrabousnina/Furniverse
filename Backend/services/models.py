"""
Pydantic Models - Data structures for the API
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class Dimensions(BaseModel):
    """Product dimensions - flexible structure based on product type"""
    width: Optional[int] = None
    height: Optional[int] = None
    depth: Optional[int] = None
    seatHeight: Optional[int] = None
    diameter: Optional[int] = None


class ColorVariant(BaseModel):
    """Color variant with all variant-specific metadata"""
    id: int
    color: str
    price: int
    rating: float
    reviewCount: int
    image: str
    images: List[str]
    inStock: bool
    dimensions: Dimensions


class Product(BaseModel):
    """Frontend-compatible product model with color variants"""
    id: int
    name: str
    category: str
    price: int
    rating: float
    reviewCount: int
    image: str
    images: List[str]
    description: str
    features: List[str]
    styles: List[str]
    colors: List[str]
    tags: List[str]
    dimensions: Dimensions
    inStock: bool
    trending: bool = False
    variants: List[ColorVariant] = []


class RecommendRequest(BaseModel):
    query: str
    category: Optional[str] = None
    limit: Optional[int] = 8


class ProductRecommendation(BaseModel):
    product_id: str
    name: str
    category: str
    price: float
    score: float
    image: Optional[str] = None


class TradeOffSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    limit: Optional[int] = 8

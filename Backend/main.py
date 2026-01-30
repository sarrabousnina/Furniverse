from fastapi import FastAPI, HTTPException, Query, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path
import sys
import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import asyncio
import json
import requests
import base64
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Add Pipeline directory to path to import qdrant_config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Pipeline'))

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PayloadSchemaType, Prefetch, Query as QdrantQuery, QueryRequest
import qdrant_config
from transformers import CLIPModel as HFCLIPModel, CLIPProcessor
import torch
import numpy as np
from user_activity import tracker, UserEvent
import embedding_tradeoff
from room_analysis import RoomAnalyzer
from product_comparison import ProductComparator
from tripo_generator import TripoGenerator


# ============================================================================
# Pydantic Models - Match Frontend Product Structure Exactly
# ============================================================================

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

# Initialize Qdrant client and models
qdrant_client = None
clip_model = None
clip_processor = None
product_comparator = None

app = FastAPI(title="Furniverse AI API")

# Mount static files for temporary images
temp_images_dir = Path("temp_images")
temp_images_dir.mkdir(exist_ok=True)
app.mount("/temp_images", StaticFiles(directory="temp_images"), name="temp_images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development (mobile access)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global repository, qdrant_client, clip_model, clip_processor, room_analyzer, product_comparator

    # Initialize CSV repository FIRST
    csv_path = Path(__file__).parent.parent / "Data" / "processed" / "products.csv"
    try:
        repository = CSVProductRepository(str(csv_path))
        print(f"[OK] Repository initialized with {len(repository.get_all())} products")
    except Exception as e:
        print(f"[ERROR] Failed to initialize repository: {e}")
        raise

    # Initialize Qdrant and CLIP for AI recommendations
    try:
        global qdrant_client, clip_model, clip_processor, product_comparator, room_analyzer
        
        qdrant_client = QdrantClient(
            url=qdrant_config.QDRANT_URL,
            api_key=qdrant_config.QDRANT_API_KEY
        )

        # Load CLIP model for text encoding (produces 512-dim embeddings)
        print("Loading CLIP model...")
        clip_model = HFCLIPModel.from_pretrained('openai/clip-vit-base-patch32')
        clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')

        # Initialize embedding-based trade-off system
        try:
            embedding_tradeoff.initialize_embedding_system(clip_model, clip_processor)
        except Exception as e:
            print(f"⚠️ Failed to initialize embedding trade-off system: {e}")
            import traceback
            traceback.print_exc()

        # Create indexes for filtering fields
        try:
            qdrant_client.create_payload_index(
                collection_name=qdrant_config.COLLECTION_PRODUCTS,
                field_name="category",
                field_schema=PayloadSchemaType.KEYWORD
            )
            print("✅ Created category index")
        except Exception as e:
            print(f"Category index: {e}")

        try:
            qdrant_client.create_payload_index(
                collection_name=qdrant_config.COLLECTION_PRODUCTS,
                field_name="price",
                field_schema=PayloadSchemaType.FLOAT
            )
            print("✅ Created price index")
        except Exception as e:
            print(f"Price index: {e}")

        # Initialize room analyzer (optional - may fail if model missing)
        try:
            room_analyzer = RoomAnalyzer(clip_model, clip_processor, qdrant_client)
            print("✅ Room analyzer initialized")
        except Exception as e:
            print(f"⚠️ Room analyzer not available: {e}")
            room_analyzer = None
        
        # Initialize product comparator (independent of room analyzer)
        try:
            product_comparator = ProductComparator(clip_model, clip_processor)
            print("✅ Product comparator initialized")
        except Exception as e:
            print(f"⚠️ Product comparator failed to initialize: {e}")
            product_comparator = None
        
        print("✅ Connected to Qdrant Cloud and loaded CLIP model")
    except Exception as e:
        print(f"❌ Failed to initialize AI models: {e}")
        print("⚠️ AI recommendations will not be available")
        import traceback
        traceback.print_exc()


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


# ============================================================================
# Trade-off Recommendation System
# ============================================================================

class TradeOffSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    limit: Optional[int] = 8


def extract_user_preferences(query: str, query_embedding: np.ndarray = None) -> dict:
    """
    Extract user preferences from natural language query using CLIP embeddings

    Uses semantic similarity instead of hardcoded keyword matching

    Args:
        query: User's natural language query
        query_embedding: Pre-computed CLIP embedding (optional, will compute if not provided)

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

    Uses semantic similarity for explainability instead of hardcoded rules

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


# ============================================================================
# Category Mapping - CSV categories to Frontend categories
# ============================================================================

CATEGORY_MAP = {
    # Sofas (95 products)
    "Three-seat sofas": "sofas",
    "Loveseats": "sofas",
    "Sectionals": "sofas",
    "Sofas with chaise lounge": "sofas",
    "Sectional sleeper sofas": "sofas",
    
    # Chairs (8 products)
    "Dining chairs": "chairs",
    "Office chairs": "chairs",
    "Desk chairs for home": "chairs",
    "Upholstered chairs": "chairs",
    "Stools": "chairs",
    
    # Tables (16 products)
    "Dining table sets for 4": "tables",
    "Dining table sets for 6": "tables",
    "Dining table sets for 10": "tables",
    "Small dining table sets for 2": "tables",
    "2 person dining tables": "tables",
    "Desks for home": "tables",
    "MITTZON office desks": "tables",
    
    # Beds (24 products)
    "Bed frames": "beds",
    "Bed frames with storage": "beds",
    "Upholstered beds": "beds",
    "Twin beds & single beds": "beds",
    "Foam mattresses": "beds",
    "Spring & hybrid mattresses": "beds",
    
    # Storage (25 products)
    "Storage shelves & shelving units": "storage",
    "Cube storage": "storage",
    "Cabinets, hutches & cupboards": "storage",
    "Kids boxes & baskets": "storage",
    "TROFAST combinations": "storage",
    "SMÅSTAD combinations": "storage",
    "Kids dressers & chest of drawers": "storage",
    "Toy boxes & shelves": "storage",
    
    # Bookcases (49 products)
    "Bookshelves & bookcases": "bookcases",
    "Display shelves & picture ledges": "bookcases",
    
    # TV & Media (67 products)
    "TV stands & benches": "tv-media",
    "TV & media storage": "tv-media",
    "BESTÅ TV benches": "tv-media",
    "BESTÅ frames": "tv-media",
    "BESTÅ sideboards": "tv-media",
    
    # Lighting (9 products)
    "Pendant lighting": "lighting",
    "Table lamps": "lighting",
    "Desk lamps": "lighting",
    "Ceiling lamps": "lighting",
    "LED lamps": "lighting",
    "Lamp shades": "lighting",
    "LED strip lights": "lighting",
    
    # Textiles (73 products)
    "Throw pillow covers": "textiles",
    "Pillow inserts": "textiles",
    "Accent & throw pillows": "textiles",
    
    # Decoration / Electronics (37 products)
    "Cable management & cord organizers": "decoration",
    "Rechargeable batteries & battery chargers": "decoration",
    "Bluetooth speakers": "decoration",
    "Wireless chargers & accessories": "decoration",
    "USB chargers, portable chargers & more": "decoration",
    "Wooden toys": "decoration",
}


# ============================================================================
# Repository Pattern - Easy to swap CSV for Qdrant later
# ============================================================================

class ProductRepository(ABC):
    """Abstract base class for product data sources"""
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        """Get all products"""
        pass
    
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        pass
    
    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """Get products by category"""
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Product]:
        """Search products (placeholder for future vector search)"""
        pass


class CSVProductRepository(ProductRepository):
    """CSV-based product repository - temporary until Qdrant is ready"""
    
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.products: List[Product] = []
        self._load_data()
    
    def _load_data(self):
        """Load and transform CSV data into Product models"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        try:
            df = pd.read_csv(self.csv_path)
            self.products = [self._transform_row(row) for _, row in df.iterrows()]
            print(f"[OK] Loaded {len(self.products)} products from CSV")
        except Exception as e:
            raise RuntimeError(f"Failed to load CSV: {e}")
    
    def _transform_row(self, row: pd.Series) -> Product:
        """Transform CSV row to frontend Product structure"""
        
        # Build dimensions object, excluding zero/null values
        dimensions_dict = {}
        if pd.notna(row.get('width')) and row.get('width', 0) > 0:
            dimensions_dict['width'] = int(row['width'])
        if pd.notna(row.get('height')) and row.get('height', 0) > 0:
            dimensions_dict['height'] = int(row['height'])
        if pd.notna(row.get('depth')) and row.get('depth', 0) > 0:
            dimensions_dict['depth'] = int(row['depth'])
        
        # Split pipe-delimited strings into arrays
        images = row['images'].split('|') if pd.notna(row.get('images')) and row['images'] else [row['image']]
        features = row['features'].split('|') if pd.notna(row.get('features')) and row['features'] else []
        # Styles are comma-separated in CSV, split and clean them
        styles_raw = row.get('styles', '')
        styles = [s.strip() for s in str(styles_raw).split(',') if s.strip()] if pd.notna(styles_raw) and styles_raw else []
        tags = row['tags'].split('|') if pd.notna(row.get('tags')) and row['tags'] else []
        
        # Colors: split comma-separated values
        colors_raw = row.get('colors', '')
        colors = [c.strip() for c in str(colors_raw).split(',') if c.strip()] if pd.notna(colors_raw) and colors_raw else []
        
        # Map category to frontend category (strip whitespace for clean matching)
        raw_category = str(row['category']).strip()
        category = CATEGORY_MAP.get(raw_category, raw_category)
        
        # Convert string booleans to actual booleans
        # Note: inStock column no longer exists in new CSV, default to True
        in_stock = True
        trending = str(row.get('trending', 'False')).lower() == 'true'
        
        return Product(
            id=int(row['id']),
            name=row['name'],
            category=category,
            price=int(row['price']),
            rating=float(row['rating']),
            reviewCount=int(row['reviewCount']),
            image=row['image'],
            images=images,
            description=row['description'],
            features=features,
            styles=styles,
            colors=colors,
            tags=tags,
            dimensions=Dimensions(**dimensions_dict),
            inStock=in_stock,
            trending=trending
        )
    
    def get_all(self) -> List[Product]:
        """Get all products (each variant listed separately)"""
        return self.products
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID (returns individual product)"""
        for product in self.products:
            if product.id == product_id:
                return product
        return None
    
    def get_by_category(self, category: str) -> List[Product]:
        """Get products by category (case-insensitive, each variant listed separately)"""
        category_lower = category.lower()
        return [p for p in self.products if p.category.lower() == category_lower]
    
    def search(self, query: str) -> List[Product]:
        """Simple text search - placeholder for future vector search (each variant listed separately)"""
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            # Search in name, description, tags, styles
            searchable = f"{product.name} {product.description} {' '.join(product.tags)} {' '.join(product.styles)}".lower()
            if query_lower in searchable:
                results.append(product)
        
        return results


# ============================================================================
# FastAPI Application Setup
# ============================================================================



# Initialize repository and AI models on startup
repository: Optional[ProductRepository] = None
qdrant_client = None
clip_model = None
clip_processor = None
room_analyzer = None


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "Furniverse AI API is running",
        "products_loaded": len(repository.get_all()) if repository else 0,
        "ai_enabled": qdrant_client is not None and clip_model is not None
    }


@app.get("/products", response_model=List[Product])
def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query")
):
    """
    Get all products, optionally filtered by category or search query
    
    - **category**: Filter by product category (e.g., "Sofas", "Tables", "Lamps")
    - **search**: Search products by keywords
    """
    if not repository:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    
    # Category filter
    if category:
        products = repository.get_by_category(category)
        if not products:
            return []  # Return empty array if no products found
        return products
    
    # Search filter
    if search:
        return repository.search(search)
    
    # Return all products
    return repository.get_all()


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    """
    Get a single product by ID
    
    - **product_id**: The unique product identifier
    """
    if not repository:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    
    product = repository.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    
    return product


@app.get("/categories")
def get_categories():
    """Get list of all available categories"""
    if not repository:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    
    categories = set(p.category for p in repository.get_all())
    return {"categories": sorted(list(categories))}



@app.post("/recommend/text", response_model=List[ProductRecommendation])
def recommend_by_text(request: RecommendRequest):
    """
    Recommend products based on text query using CLIP text embeddings
    """
    if not qdrant_client or not clip_model or not clip_processor:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Generate CLIP text embedding for the query (512 dims)
        inputs = clip_processor(text=[request.query], return_tensors="pt", padding=True, truncation=True)
        text_features = clip_model.get_text_features(**inputs)
        query_embedding = text_features.detach().numpy()[0].tolist()
        
        # Search in Qdrant using text_clip vectors (512 dims) - FIXED: was using image_clip
        search_filter = None
        if request.category and request.category != 'all':
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=request.category)
                    )
                ]
            )
        
        search_results = qdrant_client.search(
            collection_name=qdrant_config.COLLECTION_PRODUCTS,
            query_vector=("text_clip", query_embedding),
            limit=request.limit or 8,
            query_filter=search_filter,
            with_payload=True
        )
        
        # Format results
        recommendations = []
        for result in search_results:
            payload = result.payload
            recommendations.append(ProductRecommendation(
                product_id=payload.get('product_id'),
                name=payload.get('name'),
                category=payload.get('category'),
                price=payload.get('price'),
                score=result.score,
                image=payload.get('image')
            ))
        
        return recommendations
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/recommend/similar/{product_id}", response_model=List[ProductRecommendation])
def recommend_similar(product_id: str, limit: int = 8):
    """
    Find similar products using graph embeddings
    """
    if not qdrant_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Convert product_id to integer (Qdrant uses int IDs)
        product_id_int = int(product_id) if product_id.isdigit() else hash(product_id) % (2**31)
        
        # Get the product's graph embedding
        product_data = qdrant_client.retrieve(
            collection_name=qdrant_config.COLLECTION_PRODUCTS,
            ids=[product_id_int],
            with_vectors=["graph"]
        )
        
        if not product_data or len(product_data) == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get the graph vector
        graph_vector = product_data[0].vector.get("graph")
        
        if not graph_vector:
            raise HTTPException(status_code=404, detail="Graph embedding not found for this product")
        
        # Search for similar products using graph embeddings
        search_results = qdrant_client.search(
            collection_name=qdrant_config.COLLECTION_PRODUCTS,
            query_vector=("graph", graph_vector),
            limit=limit + 1,  # +1 to account for the product itself
            with_payload=True
        )
        
        # Format results (exclude the queried product itself)
        recommendations = []
        for result in search_results:
            result_product_id = str(result.payload.get('product_id'))
            if result_product_id == product_id:
                continue
            
            recommendations.append(ProductRecommendation(
                product_id=result.payload.get('product_id'),
                name=result.payload.get('name'),
                category=result.payload.get('category'),
                price=result.payload.get('price'),
                score=result.score,
                image=result.payload.get('image')
            ))
        
        return recommendations[:limit]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/recommend/fusion")
def fusion_recommend(request: RecommendRequest):
    """
    Multimodal fusion search - combines CLIP text, graph, and color embeddings
    
    Uses weighted combination:
    - 60% CLIP text/image (semantic understanding)
    - 30% Graph embeddings (style relationships)  
    - 10% Color (if color keywords detected)
    
    This is the most sophisticated search strategy
    """
    if not qdrant_client or not clip_model or not clip_processor:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        import re
        
        # Extract budget
        budget_match = re.search(r'under\s+\$?(\d+)', request.query.lower())
        max_price = float(budget_match.group(1)) if budget_match else None
        
        # Dataset-specific color keywords (28 colors from CSV analysis)
        color_keywords = ['white', 'black', 'gray', 'grey', 'brown', 'beige', 'blue', 'dark blue', 
                         'light blue', 'turquoise', 'green', 'dark green', 'light green', 'red', 
                         'pink', 'purple', 'yellow', 'orange', 'natural', 'oak', 'walnut', 'birch',
                         'anthracite', 'off-white', 'cream', 'multicolor', 'transparent', 'gold']
        
        # Extract materials/colors
        materials = []
        colors = []
        material_keywords = ['leather', 'velvet', 'fabric', 'wood', 'metal', 'cotton', 'linen']
        query_lower = request.query.lower()
        
        for material in material_keywords:
            if material in query_lower:
                materials.append(material)
        
        for color in color_keywords:
            if color in query_lower:
                colors.append(color)
        
        # Generate CLIP text embedding with color emphasis
        query_text = request.query
        if colors:
            # Boost color keywords by repeating them
            color_boost = " ".join(colors * 3)
            query_text = f"{request.query} {color_boost}"
        
        inputs = clip_processor(text=[query_text], return_tensors="pt", padding=True, truncation=True)
        text_features = clip_model.get_text_features(**inputs)
        clip_embedding = text_features.detach().numpy()[0]
        
        # Normalize CLIP embedding
        clip_embedding = clip_embedding / np.linalg.norm(clip_embedding)
        
        # Build filters
        filters = []
        if request.category and request.category != 'all':
            filters.append(FieldCondition(key="category", match=MatchValue(value=request.category)))
        if max_price:
            filters.append(FieldCondition(key="price", range={"lte": max_price}))
        
        search_filter = Filter(must=filters) if filters else None
        
        # FUSION SEARCH: Use Qdrant's query with prefetch for multi-vector fusion
        # This searches across multiple vector spaces and fuses results
        try:
            from qdrant_client.models import ScoredPoint
            
            # Primary search: CLIP text embeddings (50% weight) - FIXED: was using image_clip
            clip_results = qdrant_client.search(
                collection_name=qdrant_config.COLLECTION_PRODUCTS,
                query_vector=("text_clip", clip_embedding.tolist()),
                limit=20,  # Get more candidates for fusion
                query_filter=search_filter,
                with_payload=True,
                score_threshold=0.2
            )
            
            # Secondary search: Graph embeddings (30% weight)
            # Get graph embedding from top CLIP match
            graph_results = []
            if clip_results and len(clip_results) > 0:
                ref_product_id = str(clip_results[0].payload.get('product_id'))
                ref_product_id_int = int(ref_product_id) if ref_product_id.isdigit() else hash(ref_product_id) % (2**31)
                
                try:
                    product_data = qdrant_client.retrieve(
                        collection_name=qdrant_config.COLLECTION_PRODUCTS,
                        ids=[ref_product_id_int],
                        with_vectors=["graph"]
                    )
                    
                    if product_data and len(product_data) > 0:
                        graph_vector = product_data[0].vector.get("graph")
                        if graph_vector:
                            graph_results = qdrant_client.search(
                                collection_name=qdrant_config.COLLECTION_PRODUCTS,
                                query_vector=("graph", graph_vector),
                                limit=20,
                                query_filter=search_filter,
                                with_payload=True
                            )
                except:
                    pass
            
            # FUSION: Combine results with weighted scoring
            # Create a dictionary to track combined scores
            fused_products = {}
            
            # Add CLIP results with 60% weight
            for result in clip_results:
                product_id = result.payload.get('product_id')
                fused_products[product_id] = {
                    'payload': result.payload,
                    'score': result.score * 0.6,
                    'clip_score': result.score,
                    'graph_score': 0.0
                }
            
            # Add graph results with 30% weight
            for result in graph_results:
                product_id = result.payload.get('product_id')
                if product_id in fused_products:
                    fused_products[product_id]['score'] += result.score * 0.3
                    fused_products[product_id]['graph_score'] = result.score
                else:
                    fused_products[product_id] = {
                        'payload': result.payload,
                        'score': result.score * 0.3,
                        'clip_score': 0.0,
                        'graph_score': result.score
                    }
            
            # Sort by fused score
            sorted_products = sorted(
                fused_products.values(),
                key=lambda x: x['score'],
                reverse=True
            )[:request.limit or 8]
            
            # Build response
            response = {
                "query": request.query,
                "strategy": "multimodal_fusion",
                "explanation": f"Using AI-powered multimodal fusion: combining semantic understanding (60%), style relationships (30%), and visual features for best results",
                "budget_limit": max_price,
                "fusion_weights": {
                    "clip_semantic": 0.6,
                    "graph_style": 0.3,
                    "color_palette": 0.1
                },
                "products": []
            }
            
            # Add friendly message if using substitutes
            if materials and max_price and len(sorted_products) > 0:
                # Check if top products match the material
                has_exact_material = False
                for p in sorted_products[:3]:
                    tags = p['payload'].get('tags', [])
                    if any(mat in ' '.join(tags).lower() for mat in materials):
                        has_exact_material = True
                        break
                
                if not has_exact_material:
                    material_str = " or ".join(materials)
                    response["explanation"] = (
                        f"Sorry, we don't have {material_str} products at ${max_price}, "
                        f"but here are similar alternatives with different materials. "
                        f"Using multimodal AI fusion for best style matches!"
                    )
            
            # Format products
            for item in sorted_products:
                payload = item['payload']
                response["products"].append({
                    "product_id": payload.get('product_id'),
                    "name": payload.get('name'),
                    "category": payload.get('category'),
                    "price": payload.get('price'),
                    "score": round(item['score'], 4),
                    "clip_score": round(item['clip_score'], 4),
                    "graph_score": round(item['graph_score'], 4),
                    "image": payload.get('image'),
                    "description": payload.get('description', '')[:100],
                    "tags": payload.get('tags', []),
                    "colors": payload.get('colors', [])
                })
            
            return response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fusion search failed: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/recommend/smart")
def smart_recommend(request: RecommendRequest):
    """
    Smart recommendation with transparent compromise analysis
    
    No hard cutoffs - just explain what you gain and lose with each option:
    - Perfect matches: ≥0.67 similarity + within budget + matches color/material requirements
    - Alternatives: ≥0.67 similarity + within budget + wrong color/missing materials (compromises explained)
    - Over-budget options: ≥0.67 similarity + over budget (with price compromise)
    
    Each product shows specific trade-offs against user requirements
    """
    
    def parse_user_requirements(query_text):
        """Extract user requirements from query"""
        import re
        query_lower = query_text.lower()
        
        requirements = {
            'budget': None,
            'colors': [],
            'materials': [],
            'styles': [],
            'sizes': [],
            'features': [],
            'raw_query': query_text
        }
        
        # Budget
        budget_match = re.search(r'under\s+\$?(\d+)', query_lower)
        if budget_match:
            requirements['budget'] = float(budget_match.group(1))
        
        # Colors
        color_keywords = ['blue', 'red', 'white', 'black', 'gray', 'grey', 'green', 'yellow', 'pink', 'purple', 'brown', 'beige', 'orange']
        for color in color_keywords:
            if color in query_lower:
                requirements['colors'].append(color)
        
        # Materials
        material_keywords = ['leather', 'velvet', 'fabric', 'wood', 'metal', 'cotton', 'linen', 'suede', 'wool']
        for material in material_keywords:
            if material in query_lower:
                requirements['materials'].append(material)
        
        # Styles
        style_keywords = ['modern', 'contemporary', 'traditional', 'rustic', 'industrial', 'scandinavian', 'minimalist', 'vintage']
        for style in style_keywords:
            if style in query_lower:
                requirements['styles'].append(style)
        
        # Sizes
        size_keywords = ['large', 'small', 'compact', 'spacious', 'sectional', 'oversized']
        for size in size_keywords:
            if size in query_lower:
                requirements['sizes'].append(size)
        
        # Features
        feature_keywords = ['storage', 'adjustable', 'convertible', 'sleeper', 'reclining', 'chaise', 'comfortable', 'comfy']
        for feature in feature_keywords:
            if feature in query_lower:
                requirements['features'].append(feature)
        
        return requirements
    
    def analyze_compromises(product, user_reqs, similarity_score):
        """
        Analyze what compromises this product requires vs user requirements
        Returns natural language advantages and disadvantages
        """
        advantages = []
        disadvantages = []
        compromise_score = 0  # Higher = better match
        
        product_name = product.get('name', '').lower()
        product_desc = product.get('description', '').lower()
        product_colors = [c.lower() for c in product.get('colors', [])]
        product_tags = [t.lower() for t in product.get('tags', [])]
        product_price = product.get('price', 0)
        
        # Budget Analysis
        if user_reqs['budget']:
            price_diff = product_price - user_reqs['budget']
            price_percent = (price_diff / user_reqs['budget'] * 100) if user_reqs['budget'] > 0 else 0
            
            if price_diff <= 0:
                under_by = abs(price_diff)
                if under_by > user_reqs['budget'] * 0.1:  # More than 10% under
                    advantages.append(f"${under_by:.0f} under budget ({abs(price_percent):.0f}% savings)")
                    compromise_score += 10
                else:
                    advantages.append(f"Within budget")
                    compromise_score += 15
            else:
                disadvantages.append(f"${price_diff:.0f} over budget (+{price_percent:.0f}%)")
                compromise_score -= price_percent / 10  # Penalty scales with overage
        
        # Color Analysis
        if user_reqs['colors']:
            requested_colors = user_reqs['colors']
            matching_colors = [c for c in requested_colors if any(c in pc for pc in product_colors)]
            
            if matching_colors:
                advantages.append(f"Exact {', '.join(matching_colors)} color match")
                compromise_score += 10 * len(matching_colors)
            else:
                if product_colors:
                    disadvantages.append(f"Different color: {', '.join(product_colors[:2])}")
                    compromise_score -= 8
                else:
                    disadvantages.append(f"Color not specified")
                    compromise_score -= 5
        
        # Material Analysis
        if user_reqs['materials']:
            for material in user_reqs['materials']:
                if material in product_desc or material in product_name or any(material in tag for tag in product_tags):
                    advantages.append(f"Has requested {material}")
                    compromise_score += 8
                else:
                    disadvantages.append(f"Missing {material}")
                    compromise_score -= 6
        
        # Style Analysis
        if user_reqs['styles']:
            for style in user_reqs['styles']:
                if style in product_desc or style in product_name or any(style in tag for tag in product_tags):
                    advantages.append(f"{style.capitalize()} style as requested")
                    compromise_score += 5
        
        # Size Analysis
        if user_reqs['sizes']:
            for size in user_reqs['sizes']:
                if size in product_name or size in product_desc:
                    advantages.append(f"{size.capitalize()} size as requested")
                    compromise_score += 5
        
        # Features Analysis
        if user_reqs['features']:
            for feature in user_reqs['features']:
                if feature in product_desc or feature in product_name or any(feature in tag for tag in product_tags):
                    advantages.append(f"Has {feature} feature")
                    compromise_score += 5
        
        # General product advantages (even if not requested)
        quality_indicators = ['premium', 'luxury', 'durable', 'solid wood', 'genuine', 'high-quality']
        for indicator in quality_indicators:
            if indicator in product_desc or any(indicator in tag for tag in product_tags):
                advantages.append(f"Premium quality ({indicator})")
                break
        
        feature_indicators = ['storage', 'chaise', 'sectional', 'convertible', 'sleeper']
        found_features = [f for f in feature_indicators if f in product_name or f in product_desc]
        if found_features and not any(f in user_reqs['features'] for f in found_features):
            advantages.append(f"Extra features: {', '.join(found_features[:2])}")
            compromise_score += 3
        
        # Similarity score impact
        compromise_score += similarity_score * 50  # Similarity is key factor
        
        # Generate natural summary
        if not disadvantages:
            if len(advantages) >= 3:
                summary = f"Perfect match: {advantages[0].lower()}, {advantages[1].lower()}, and {len(advantages)-2} more benefits"
            elif len(advantages) == 2:
                summary = f"Great match: {advantages[0].lower()} and {advantages[1].lower()}"
            elif len(advantages) == 1:
                summary = f"Good match: {advantages[0].lower()}"
            else:
                summary = "Solid option that meets your needs"
        else:
            adv_text = advantages[0].lower() if advantages else "matches your search"
            disadv_text = disadvantages[0].lower()
            summary = f"Trade-off: {adv_text}, but {disadv_text}"
        
        return {
            'summary': summary,
            'advantages': advantages if advantages else ['Matches your search criteria'],
            'disadvantages': disadvantages if disadvantages else [],
            'compromise_score': round(compromise_score, 2)
        }
    
    # Main function logic
    if not qdrant_client or not clip_model or not clip_processor:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Parse user requirements
        user_reqs = parse_user_requirements(request.query)
        max_price = user_reqs['budget']
        
        # Generate query embedding
        inputs = clip_processor(text=[request.query], return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            text_features = clip_model.get_text_features(**inputs)
            query_embedding = text_features.numpy()[0].tolist()
        
        # Thresholds
        THRESHOLD_MINIMUM = 0.67  # Minimum to show any product (same category)
        # No "alternative" tier - below 0.67 = different product category (TV vs sofa)
        
        # Build category filter
        
        # Build category filter
        filters = []
        if request.category and request.category != 'all':
            filters.append(FieldCondition(key="category", match=MatchValue(value=request.category)))
        
        search_filter = Filter(must=filters) if filters else None
        
        # Get candidates
        all_results = qdrant_client.search(
            collection_name=qdrant_config.COLLECTION_PRODUCTS,
            query_vector=("text_clip", query_embedding),
            limit=50,
            query_filter=search_filter,
            with_payload=True,
            score_threshold=THRESHOLD_MINIMUM  # Only ≥0.67
        )
        
        # Categorize products with compromise analysis
        perfect_matches = []  # ≥0.67 + within budget + matches color/material
        alternatives = []  # ≥0.67 + within budget + wrong color/material
        over_budget_options = []  # ≥0.67 + over budget
        
        for result in all_results:
            payload = result.payload
            price = payload.get('price', 0)
            similarity = result.score
            
            product_data = {
                "product_id": payload.get('product_id'),
                "name": payload.get('name'),
                "category": payload.get('category'),
                "price": price,
                "score": round(similarity, 4),
                "image": payload.get('image'),
                "description": payload.get('description', '')[:100],
                "tags": payload.get('tags', []),
                "colors": payload.get('colors', [])
            }
            
            # Analyze compromises for this product
            compromise_analysis = analyze_compromises(product_data, user_reqs, similarity)
            product_data['compromise'] = compromise_analysis
            
            # Check if color/material matches user requirements
            has_color_mismatch = False
            has_material_mismatch = False
            
            if user_reqs['colors']:
                product_colors = [c.lower() for c in payload.get('colors', [])]
                requested_colors = [c.lower() for c in user_reqs['colors']]
                matching_colors = [c for c in requested_colors if any(c in pc for pc in product_colors)]
                if not matching_colors:
                    has_color_mismatch = True
            
            if user_reqs['materials']:
                product_desc = payload.get('description', '').lower()
                requested_materials = [m.lower() for m in user_reqs['materials']]
                matching_materials = [m for m in requested_materials if m in product_desc]
                if not matching_materials:
                    has_material_mismatch = True
            
            # Categorize based on budget, color, and material
            if max_price is None or price <= max_price:
                # Within budget
                if has_color_mismatch or has_material_mismatch:
                    # Within budget but wrong color/material -> alternatives
                    alternatives.append(product_data)
                else:
                    # Within budget and correct color/material -> perfect match
                    perfect_matches.append(product_data)
            else:
                # Over budget
                over_budget_options.append(product_data)
        
        # Sort by compromise score (best compromises first)
        perfect_matches.sort(key=lambda x: x['compromise']['compromise_score'], reverse=True)
        alternatives.sort(key=lambda x: x['compromise']['compromise_score'], reverse=True)
        over_budget_options.sort(key=lambda x: x['compromise']['compromise_score'], reverse=True)
        
        # Limit results
        perfect_matches = perfect_matches[:10]
        alternatives = alternatives[:5]
        over_budget_options = over_budget_options[:5]
        
        # Build response with explanations
        response = {
            "query": request.query,
            "user_requirements": user_reqs,
            "perfect_matches": perfect_matches,
            "alternatives": alternatives,
            "over_budget_options": over_budget_options,
            "strategy": "compromise_analysis",
            "explanation": ""
        }
        
        # Generate smart explanation
        total_perfect = len(perfect_matches)
        total_alternatives = len(alternatives)
        total_over_budget = len(over_budget_options)
        
        if total_perfect >= 5:
            response["explanation"] = f"Found {total_perfect} great matches within your budget!"
        elif total_perfect > 0:
            response["explanation"] = f"Found {total_perfect} good matches"
            if total_alternatives > 0:
                response["explanation"] += f" and {total_alternatives} alternatives with different colors/materials"
            if total_over_budget > 0:
                response["explanation"] += f" and {total_over_budget} options slightly over budget"
        elif total_alternatives > 0:
            response["explanation"] = f"Found {total_alternatives} alternatives (different colors/materials) within budget"
            if total_over_budget > 0:
                response["explanation"] += f" and {total_over_budget} options over budget"
        elif total_over_budget > 0:
            response["explanation"] = f"Found {total_over_budget} excellent matches just above your budget - small compromise for great results"
        else:
            response["explanation"] = "No products found with ≥0.67 similarity (same category). Try adjusting your search."
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/recommend/image")
async def recommend_by_image(
    file: UploadFile = File(...),
    category: Optional[str] = None,
    limit: int = 8
):
    """
    Search products by uploaded image using CLIP image embeddings
    
    Accepts an image file and returns visually similar products by:
    1. Encoding the uploaded image using the same CLIP model used for product images
    2. Searching Qdrant's image_clip vector (512d) for similar products
    3. Applying category filters if specified
    
    Args:
        file: Uploaded image file (JPEG, PNG, WebP)
        category: Optional category filter (e.g., 'sofas', 'tables')
        limit: Maximum number of results to return (default: 8)
    
    Returns:
        List of visually similar products with similarity scores
    """
    if not qdrant_client or not clip_model or not clip_processor:
        raise HTTPException(status_code=503, detail="AI service not initialized")
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image (JPEG, PNG, WebP)")
        
        # Read uploaded file and convert to PIL Image
        image_bytes = await file.read()
        
        # Validate file size (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image file too large (max 10MB)")
        
        try:
            image = Image.open(BytesIO(image_bytes)).convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # Generate CLIP image embedding (512 dimensions)
        inputs = clip_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)
        query_embedding = image_features.detach().numpy()[0].tolist()
        
        # Build category filter
        filters = []
        if category and category != 'all':
            filters.append(FieldCondition(key="category", match=MatchValue(value=category)))
        
        search_filter = Filter(must=filters) if filters else None
        
        # Search Qdrant with image_clip vector
        results = qdrant_client.search(
            collection_name=qdrant_config.COLLECTION_PRODUCTS,
            query_vector=("image_clip", query_embedding),
            limit=limit,
            query_filter=search_filter,
            with_payload=True,
            score_threshold=0.5  # Reasonable threshold for visual similarity
        )
        
        # Format response
        recommendations = []
        for result in results:
            payload = result.payload
            recommendations.append({
                "product_id": payload.get('product_id'),
                "name": payload.get('name'),
                "category": payload.get('category'),
                "price": payload.get('price'),
                "score": round(result.score, 4),
                "image": payload.get('image'),
                "description": payload.get('description', '')[:150]
            })
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image search failed: {str(e)}")


@app.post("/search/tradeoffs")
def search_with_tradeoffs(request: TradeOffSearchRequest):
    """
    Trade-off aware search with explainability

    This endpoint:
    1. Extracts user preferences from the query (budget, material, style, color, comfort)
    2. Searches Qdrant for semantically similar products
    3. Calculates trade-offs for each product (what you gain vs what you lose)
    4. Returns products with detailed explainability

    Example query: "comfy modern red leather couch budget 500"

    Returns:
        - exact_matches: Products that match all preferences
        - trade_offs: Products with compromises (explained)
        - user_preferences: Extracted preferences from query
    """
    if not qdrant_client or not clip_model or not clip_processor:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Step 1: Generate CLIP text embedding (used for both search and extraction)
        inputs = clip_processor(text=[request.query], return_tensors="pt", padding=True, truncation=True)
        text_features = clip_model.get_text_features(**inputs)
        query_embedding = text_features.detach().numpy()[0]  # Keep as numpy array
        query_embedding_list = query_embedding.tolist()  # Convert for Qdrant

        # Step 2: Extract user preferences using CLIP embeddings
        preferences = extract_user_preferences(request.query, query_embedding)

        # Step 3: Build filters
        filters = []

        if request.category and request.category != 'all':
            filters.append(FieldCondition(key="category", match=MatchValue(value=request.category)))

        # Budget as hard constraint
        if preferences.get("budget"):
            filters.append(FieldCondition(key="price", range={"lte": preferences["budget"]}))

        search_filter = Filter(must=filters) if filters else None

        # Step 4: Primary search with text_clip
        results = qdrant_client.search(
            collection_name=qdrant_config.COLLECTION_PRODUCTS,
            query_vector=("image_clip", query_embedding_list),
            limit=request.limit or 10,
            query_filter=search_filter,
            with_payload=True,
            score_threshold=0.2
        )

        # Step 5: Calculate trade-offs for each product using embeddings
        exact_matches = []
        trade_offs = []

        for result in results:
            payload = result.payload

            # Build product dict for trade-off calculation
            product = {
                "product_id": payload.get('product_id'),
                "name": payload.get('name'),
                "category": payload.get('category'),
                "price": payload.get('price'),
                "score": round(result.score, 4),
                "image": payload.get('image'),
                "description": payload.get('description', ''),
                "tags": payload.get('tags', []),
                "styles": payload.get('styles', []),
                "colors": payload.get('colors', [])
            }

            # Calculate trade-offs using CLIP embeddings
            tradeoff_analysis = calculate_tradeoffs(product, preferences, query_embedding)

            # Add trade-off info to product
            product["tradeoff_analysis"] = tradeoff_analysis

            # Separate exact matches from trade-offs
            if not tradeoff_analysis["is_compromise"]:
                exact_matches.append(product)
            else:
                trade_offs.append(product)

        # Step 6: Build response with explainability
        response = {
            "query": request.query,
            "user_preferences": preferences,
            "total_results": len(results),
            "exact_matches": exact_matches,
            "trade_offs": trade_offs,
            "explanation": build_tradeoff_explanation(preferences, len(exact_matches), len(trade_offs)),
            "embedding_analysis": {
                "method": "clip_similarity",
                "embedding_model": "openai/clip-vit-base-patch32",
                "dimensions": 512
            }
        }

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Trade-off search failed: {str(e)}")


def build_tradeoff_explanation(preferences: dict, exact_count: int, tradeoff_count: int) -> str:
    """Build human-readable explanation for trade-off results"""

    if exact_count > 0:
        return f"Found {exact_count} perfect match(es) for your search!"

    if tradeoff_count == 0:
        return "No products found matching your criteria. Try adjusting your search or budget."

    # Build explanation for trade-offs
    explanations = []

    if preferences.get("budget") and preferences.get("material"):
        explanations.append(
            f"We couldn't find {preferences['material']} products within your ${preferences['budget']} budget. "
            f"However, we found {tradeoff_count} alternatives that offer great value!"
        )
    elif preferences.get("budget"):
        explanations.append(
            f"We found {tradeoff_count} product(s) within your ${preferences['budget']} budget. "
            f"Each one has been analyzed for trade-offs to help you decide."
        )
    else:
        explanations.append(
            f"We found {tradeoff_count} product(s) that partially match your preferences. "
            f"Check the trade-off analysis to see what you gain and lose with each option."
        )

    return " ".join(explanations)


@app.post("/recommend/color", response_model=List[ProductRecommendation])
def recommend_by_color(hex_color: str, limit: int = 8):
    """
    Recommend products by color similarity using color embeddings
    Note: This is a placeholder - you'd need to generate color embeddings from hex codes
    """
    if not qdrant_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    raise HTTPException(status_code=501, detail="Color-based search requires color embedding generation")


@app.get("/stats")
def get_stats():
    """Get statistics about indexed products"""
    if not qdrant_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        collection_info = qdrant_client.get_collection(qdrant_config.COLLECTION_PRODUCTS)
        return {
            "total_products": collection_info.points_count,
            "vectors": {
                "image_clip": 512,
                "graph": 256,
                "color": 548
            },
            "status": "ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# ============================================================================
# Product → User Recommendations (User Activity Tracking)
# ============================================================================

class TrackEventRequest(BaseModel):
    """Request model for tracking user events"""
    user_id: str
    event_type: str  # 'view', 'click', 'search'
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    search_query: Optional[str] = None


@app.post("/track")
def track_user_event(request: TrackEventRequest):
    """
    Track user interaction events (Product → User foundation)
    Stores: views, clicks, searches to build user preference profiles
    """
    try:
        event = UserEvent(
            user_id=request.user_id,
            event_type=request.event_type,
            product_id=request.product_id or "",
            product_name=request.product_name or "",
            category=request.category or "",
            price=request.price or 0.0,
            search_query=request.search_query
        )

        tracker.track_event(event)

        return {
            "status": "tracked",
            "user_id": request.user_id,
            "event_type": request.event_type,
            "timestamp": event.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track event: {str(e)}")


@app.get("/users/interested-in/{product_id}")
def find_interested_users(
    product_id: str,
    product_name: str = Query(..., description="Product name for similarity matching"),
    category: str = Query(..., description="Product category"),
    limit: int = Query(10, description="Number of users to return")
):
    """
    Product → User Recommendation: Find users who would be interested in a product

    Use case: When admin creates a discount, find users who interacted with similar products
    Uses semantic similarity between product and user preference embeddings
    """
    try:
        interested_users = tracker.find_interested_users(
            product_id=product_id,
            product_name=product_name,
            category=category,
            limit=limit
        )

        return {
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "interested_users": interested_users,
            "total_count": len(interested_users)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find interested users: {str(e)}")


@app.get("/users/{user_id}/activity")
def get_user_activity(user_id: str):
    """Get activity summary for a specific user"""
    try:
        summary = tracker.get_user_activity_summary(user_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user activity: {str(e)}")


@app.get("/users/stats")
def get_user_stats():
    """Get statistics about tracked users from Qdrant"""
    try:
        from user_activity import tracker

        # Get collection info from Qdrant
        collection_info = tracker.qdrant_client.get_collection('users')

        return {
            "total_users": collection_info.points_count,
            "total_vectors": collection_info.vectors_count,
            "users_indexed": collection_info.points_count,
            "storage": "qdrant_cloud",
            "status": "ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}")


# ============================================================================
# Room Analysis Endpoint
# ============================================================================

class RoomAnalysisRequest(BaseModel):
    """Request model for enhanced room analysis with furniture suggestions"""
    image: str  # Base64 encoded image
    room_type: Optional[str] = None  # Optional room type (Living Room, Bedroom, etc.)
    budget_min: Optional[int] = None  # Optional minimum budget per item
    budget_max: Optional[int] = None  # Optional maximum budget per item
    existing_furniture: Optional[str] = None  # Optional description of existing furniture


@app.post("/analyze/room")
def analyze_room(request: RoomAnalysisRequest):
    """Analyze room image to detect furniture, determine style, and suggest missing items"""
    if not room_analyzer:
        raise HTTPException(status_code=503, detail="Room analyzer not initialized")
    
    try:
        result = room_analyzer.analyze_room_with_suggestions(
            image_data=request.image,
            room_type=request.room_type,
            budget_min=request.budget_min,
            budget_max=request.budget_max,
            existing_furniture=request.existing_furniture
        )
        return result
    except Exception as e:
        print(f"Room analysis error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Room analysis failed: {str(e)}")


# ============================================================================
# AI Product Comparison (HACKATHON FEATURE!)
# ============================================================================

class ComparisonRequest(BaseModel):
    """Request to compare two products"""
    product_a_id: int
    product_b_id: int


@app.post("/compare/products")
def compare_products(request: ComparisonRequest):
    """
    🎯 HACKATHON FEATURE: AI-Powered Product Comparison
    
    Compare two products side-by-side with detailed AI analysis:
    - Visual similarity score (CLIP embeddings)
    - Price analysis and value proposition
    - Feature-by-feature comparison
    - Style compatibility analysis
    - AI recommendation on which to choose
    
    Perfect for users deciding between similar products!
    """
    if not product_comparator:
        raise HTTPException(status_code=503, detail="Product comparator not initialized")
    
    try:
        # Get both products from repository
        product_a = repository.get_by_id(request.product_a_id)
        product_b = repository.get_by_id(request.product_b_id)
        
        if not product_a:
            raise HTTPException(status_code=404, detail=f"Product {request.product_a_id} not found")
        if not product_b:
            raise HTTPException(status_code=404, detail=f"Product {request.product_b_id} not found")
        
        # Convert to dict for comparison
        product_a_dict = product_a.dict()
        product_b_dict = product_b.dict()
        
        # Run AI comparison
        comparison_result = product_comparator.compare_products(product_a_dict, product_b_dict)
        
        return comparison_result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


# ============================================================================
# 3D Model Generation with Tripo AI
# ============================================================================

@app.get("/check-3d-model/{product_id}")
async def check_3d_model(product_id: int):
    """Check if a 3D model exists for this product"""
    try:
        # Check if model file exists
        model_path = f"../Frontend/public/models/product-{product_id}.glb"
        if os.path.exists(model_path):
            return {
                "exists": True,
                "model_url": f"/models/product-{product_id}.glb"
            }
        return {"exists": False}
    except Exception as e:
        return {"exists": False}


@app.post("/generate-3d-model")
async def generate_3d_model(
    product_id: int,
    background_tasks: BackgroundTasks = None
):
    """Generate 3D model from product image using Tripo AI"""
    try:
        # Get Tripo API key from environment
        TRIPO_API_KEY = os.getenv("TRIPO_API_KEY")
        if not TRIPO_API_KEY:
            raise HTTPException(status_code=500, detail="TRIPO_API_KEY not configured")
        
        # Get product
        product = repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        # Initialize generator
        generator = TripoGenerator(TRIPO_API_KEY)
        
        # Generate model
        result = generator.generate_model(
            image_url=product.image,
            product_id=str(product_id),
            product_name=product.name
        )
        
        return result
    
    except Exception as e:
        print(f"Error generating 3D model: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"3D generation failed: {str(e)}")


# ============================================================================
# AI Room Visualizer with Kie.ai
# ============================================================================

# Helper endpoint to convert base64 images to accessible URLs
@app.post("/upload-temp-image")
async def upload_temp_image(image_data: dict):
    """Convert base64 image to publicly accessible URL using free image hosting"""
    try:
        base64_str = image_data.get("image", "")
        
        # Remove data URL prefix if present
        if "base64," in base64_str:
            base64_str = base64_str.split("base64,")[1]
        
        print("📤 Uploading image to image hosting service...")
        
        # Try ImgBB free API (no auth required)
        try:
            upload_response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={
                    "key": "2d4b8580fa3f6da3d6e201641a6f1e98",  # Free ImgBB API key (get your own at api.imgbb.com)
                    "image": base64_str,
                    "expiration": 600,  # 10 minutes expiration
                }
            )
            
            if upload_response.ok:
                upload_data = upload_response.json()
                if upload_data.get("success"):
                    image_url = upload_data["data"]["url"]
                    print(f"✅ Image uploaded to ImgBB: {image_url}")
                    return {
                        "success": True,
                        "url": image_url,
                    }
        except Exception as e:
            print(f"⚠️ ImgBB upload failed: {e}")
        
        # Fallback: use freeimage.host
        try:
            files = {"source": ("image.jpg", base64.b64decode(base64_str))}
            upload_response = requests.post(
                "https://freeimage.host/api/1/upload",
                data={"key": "6d207e02198a847aa98d0a2a901485a5"},
                files=files
            )
            
            if upload_response.ok:
                upload_data = upload_response.json()
                if upload_data.get("status_code") == 200:
                    image_url = upload_data["image"]["url"]
                    print(f"✅ Image uploaded to FreeImage: {image_url}")
                    return {
                        "success": True,
                        "url": image_url,
                    }
        except Exception as e:
            print(f"⚠️ FreeImage upload failed: {e}")
        
        raise HTTPException(
            status_code=500,
            detail="Failed to upload image to public hosting. For local testing, please use ngrok or cloudflare tunnel to expose your backend."
        )
    
    except Exception as e:
        print(f"Error uploading image: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class RoomVisualizerRequest(BaseModel):
    room_image_url: str
    products: list[dict]
    aspect_ratio: str = "auto"

@app.post("/room-visualizer")
async def room_visualizer(request: RoomVisualizerRequest):
    """Generate room visualization with AI-placed furniture using Kie.ai"""
    try:
        KIE_API_KEY = os.getenv("KIE_AI_API_KEY")
        if not KIE_API_KEY:
            raise HTTPException(status_code=500, detail="KIE_AI_API_KEY not configured")
        
        if not request.products:
            raise HTTPException(status_code=400, detail="At least one product is required")
        
        print(f"🎨 Starting room visualization")
        print(f"Room image: {request.room_image_url}")
        print(f"Products: {len(request.products)}")
        
        # Build input URLs: room image first, then product images
        input_urls = [request.room_image_url] + [p["image"] for p in request.products]
        
        # Build detailed prompt for furniture placement
        product_descriptions = ", ".join([
            f"furniture item {i+1} ({p['name']}) placed {p['placement']}"
            for i, p in enumerate(request.products)
        ])
        
        prompt = f"""Transform this room photo by realistically adding the furniture shown in the reference images. Place {product_descriptions}. Maintain realistic lighting, shadows, and perspective matching the room. The furniture should look naturally integrated into the space, matching the room's lighting conditions and floor perspective. Keep the room's original architecture, windows, and other elements intact. Professional interior design photography style, photorealistic result."""
        
        # Create task
        create_response = requests.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {KIE_API_KEY}"
            },
            json={
                "model": "flux-2/pro-image-to-image",
                "input": {
                    "input_urls": input_urls,
                    "prompt": prompt,
                    "aspect_ratio": request.aspect_ratio,
                    "resolution": "2K"
                }
            }
        )
        
        if not create_response.ok:
            print(f"❌ Kie AI HTTP error: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            raise HTTPException(status_code=500, detail=f"Kie AI createTask failed: {create_response.status_code}")
        
        task_data = create_response.json()
        print(f"📦 Kie AI response: {json.dumps(task_data, indent=2)}")
        
        if task_data.get("code") != 200:
            # Kie.ai uses 'msg' not 'message'
            error_msg = task_data.get('msg') or task_data.get('message', 'Unknown error')
            print(f"❌ Kie AI error code {task_data.get('code')}: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Kie AI error: {error_msg}")
        
        task_id = task_data["data"]["taskId"]
        print(f"✅ Task created: {task_id}")
        
        # Poll for completion (max 30 attempts, 10 seconds each = 5 minutes)
        for attempt in range(30):
            await asyncio.sleep(10)
            
            status_response = requests.get(
                f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                headers={"Authorization": f"Bearer {KIE_API_KEY}"}
            )
            
            if not status_response.ok:
                continue
            
            status_data = status_response.json()
            state = status_data.get("data", {}).get("state")
            
            print(f"📊 Task status (attempt {attempt + 1}): {state}")
            
            if state == "success":
                result_json = json.loads(status_data["data"].get("resultJson", "{}"))
                result_url = result_json.get("resultUrls", [None])[0]
                
                if result_url:
                    print(f"🎉 Task completed! Result URL: {result_url}")
                    return {
                        "success": True,
                        "result_url": result_url,
                        "task_id": task_id
                    }
            
            if state == "fail":
                fail_msg = status_data.get("data", {}).get("failMsg", "Unknown error")
                raise HTTPException(status_code=500, detail=f"Kie AI task failed: {fail_msg}")
        
        raise HTTPException(status_code=504, detail="Task timed out after maximum attempts")
    
    except Exception as e:
        print(f"Error in room visualizer: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"3D generation failed: {str(e)}")


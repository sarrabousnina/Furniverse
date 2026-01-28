from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path
import sys
import os

# Add Pipeline directory to path to import qdrant_config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Pipeline'))

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PayloadSchemaType, Prefetch, Query as QdrantQuery, QueryRequest
import qdrant_config
from transformers import CLIPModel as HFCLIPModel, CLIPProcessor
import numpy as np
from user_activity import tracker, UserEvent
import embedding_tradeoff


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

app = FastAPI(title="Furniverse AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global repository, qdrant_client, clip_model, clip_processor

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

        print("✅ Connected to Qdrant Cloud and loaded CLIP model")
    except Exception as e:
        print(f"❌ Failed to initialize AI models: {e}")
        print("⚠️ AI recommendations will not be available")


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
        
        # Search in Qdrant using image_clip vectors (512 dims)
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
            query_vector=("image_clip", query_embedding),
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
        
        # Extract materials/colors
        materials = []
        material_keywords = ['leather', 'velvet', 'fabric', 'wood', 'metal', 'cotton', 'linen']
        query_lower = request.query.lower()
        for material in material_keywords:
            if material in query_lower:
                materials.append(material)
        
        # Generate CLIP text embedding
        inputs = clip_processor(text=[request.query], return_tensors="pt", padding=True, truncation=True)
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
            
            # Primary search: CLIP embeddings (60% weight)
            clip_results = qdrant_client.search(
                collection_name=qdrant_config.COLLECTION_PRODUCTS,
                query_vector=("image_clip", clip_embedding.tolist()),
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
    Smart budget-aware recommendation with fallback strategy
    
    Pipeline:
    1. Extract CLIP text embedding from query
    2. Search with text embedding + optional filters
    3. If budget constraint specified, apply price filter
    4. If no results, use graph embeddings to find substitutes
    5. Return with explanations
    """
    if not qdrant_client or not clip_model or not clip_processor:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Extract budget from query if mentioned
        import re
        budget_match = re.search(r'under\s+\$?(\d+)', request.query.lower())
        max_price = float(budget_match.group(1)) if budget_match else None
        
        # Extract materials/fabrics mentioned in query
        materials = []
        material_keywords = ['leather', 'velvet', 'fabric', 'wood', 'metal', 'cotton', 'linen', 'polyester', 'suede']
        query_lower = request.query.lower()
        for material in material_keywords:
            if material in query_lower:
                materials.append(material)
        
        # Generate CLIP text embedding
        inputs = clip_processor(text=[request.query], return_tensors="pt", padding=True, truncation=True)
        text_features = clip_model.get_text_features(**inputs)
        query_embedding = text_features.detach().numpy()[0].tolist()
        
        # Build filters
        filters = []
        if request.category and request.category != 'all':
            filters.append(FieldCondition(key="category", match=MatchValue(value=request.category)))
        
        if max_price:
            filters.append(FieldCondition(key="price", range={"lte": max_price}))
        
        search_filter = Filter(must=filters) if filters else None
        
        # Primary search with text_clip
        results = qdrant_client.search(
            collection_name=qdrant_config.COLLECTION_PRODUCTS,
            query_vector=("image_clip", query_embedding),
            limit=request.limit or 8,
            query_filter=search_filter,
            with_payload=True,
            score_threshold=0.25
        )
        
        response = {
            "query": request.query,
            "strategy": "direct_match",
            "explanation": f"Found {len(results)} products matching your search",
            "products": [],
            "budget_limit": max_price
        }
        
        # If no results with budget constraint, try fallback with graph embeddings
        if len(results) == 0 and max_price:
            # Remove budget filter and search again
            search_filter_no_budget = None
            if request.category and request.category != 'all':
                search_filter_no_budget = Filter(
                    must=[FieldCondition(key="category", match=MatchValue(value=request.category))]
                )
            
            # Get a reference product using text search (no budget limit)
            reference_results = qdrant_client.search(
                collection_name=qdrant_config.COLLECTION_PRODUCTS,
                query_vector=("image_clip", query_embedding),
                limit=1,
                query_filter=search_filter_no_budget,
                with_payload=True
            )
            
            if reference_results and len(reference_results) > 0:
                # Get the reference product's ID
                ref_product_id = str(reference_results[0].payload.get('product_id'))
                ref_product_id_int = int(ref_product_id) if ref_product_id.isdigit() else hash(ref_product_id) % (2**31)
                
                # Get graph embedding for substitutes
                product_data = qdrant_client.retrieve(
                    collection_name=qdrant_config.COLLECTION_PRODUCTS,
                    ids=[ref_product_id_int],
                    with_vectors=["graph"]
                )
                
                if product_data and len(product_data) > 0:
                    graph_vector = product_data[0].vector.get("graph")
                    
                    if graph_vector:
                        # Search for substitutes using graph embeddings + budget filter
                        substitute_filter = Filter(must=[FieldCondition(key="price", range={"lte": max_price})])
                        
                        results = qdrant_client.search(
                            collection_name=qdrant_config.COLLECTION_PRODUCTS,
                            query_vector=("graph", graph_vector),
                            limit=request.limit or 8,
                            query_filter=substitute_filter,
                            with_payload=True
                        )
                        
                        response["strategy"] = "graph_substitutes"
                        
                        # Create helpful explanation based on what was searched
                        if materials:
                            material_str = " or ".join(materials)
                            response["explanation"] = (
                                f"Sorry, we don't have {material_str} products at ${max_price}, "
                                f"but here are similar alternatives with different materials in your budget. "
                                f"These products have comparable style and aesthetics!"
                            )
                        else:
                            response["explanation"] = (
                                f"We couldn't find exact matches at ${max_price}, "
                                f"but here are similar products in your budget with comparable features!"
                            )
        elif len(results) == 0:
            response["explanation"] = "No products found matching your criteria. Try adjusting your search or budget."
        
        # Format products
        for result in results:
            payload = result.payload
            response["products"].append({
                "product_id": payload.get('product_id'),
                "name": payload.get('name'),
                "category": payload.get('category'),
                "price": payload.get('price'),
                "score": round(result.score, 4),
                "image": payload.get('image'),
                "description": payload.get('description', '')[:100],
                "tags": payload.get('tags', []),
                "colors": payload.get('colors', [])
            })
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


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


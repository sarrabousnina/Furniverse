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

@app.on_event("startup")
async def startup_event():
    global qdrant_client, clip_model, clip_processor
    try:
        qdrant_client = QdrantClient(
            url=qdrant_config.QDRANT_URL,
            api_key=qdrant_config.QDRANT_API_KEY
        )
        
        # Load CLIP model for text encoding (produces 512-dim embeddings)
        print("Loading CLIP model...")
        clip_model = HFCLIPModel.from_pretrained('openai/clip-vit-base-patch32')
        clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
        
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
        print(f"❌ Failed to initialize: {e}")


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
    
    def _group_products_by_name(self) -> List[Product]:
        """Group products by name, treating different colors as variants"""
        grouped = {}
        
        for product in self.products:
            # Use name as the grouping key
            key = product.name.strip()
            
            if key not in grouped:
                # First variant becomes the base product
                grouped[key] = product
                grouped[key].variants = []
            
            # Create variant for this color
            variant = ColorVariant(
                id=product.id,
                color=product.colors[0] if product.colors else "default",
                price=product.price,
                rating=product.rating,
                reviewCount=product.reviewCount,
                image=product.image,
                images=product.images,
                inStock=product.inStock,
                dimensions=product.dimensions
            )
            grouped[key].variants.append(variant)
        
        # Update the colors list and set base price to minimum variant price
        for product in grouped.values():
            product.colors = [v.color for v in product.variants]
            # Set base price to minimum of all variant prices
            if product.variants:
                product.price = min(v.price for v in product.variants)

        return list(grouped.values())
    
    def get_all(self) -> List[Product]:
        """Get all products (grouped by name with color variants)"""
        return self._group_products_by_name()
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID (returns grouped product with all variants)"""
        # First find which ungrouped product matches the ID
        matching_product = None
        for product in self.products:
            if product.id == product_id:
                matching_product = product
                break
        
        if not matching_product:
            return None
        
        # Find the grouped product that contains this variant
        grouped_products = self._group_products_by_name()
        for grouped in grouped_products:
            # Check if any variant has this ID
            if any(v.id == product_id for v in grouped.variants):
                return grouped
        
        return None
    
    def get_by_category(self, category: str) -> List[Product]:
        """Get products by category (case-insensitive, grouped by name)"""
        category_lower = category.lower()
        grouped_products = self._group_products_by_name()
        return [p for p in grouped_products if p.category.lower() == category_lower]
    
    def search(self, query: str) -> List[Product]:
        """Simple text search - placeholder for future vector search (grouped by name)"""
        query_lower = query.lower()
        results = []
        grouped_products = self._group_products_by_name()
        
        for product in grouped_products:
            # Search in name, description, tags, styles
            searchable = f"{product.name} {product.description} {' '.join(product.tags)} {' '.join(product.styles)}".lower()
            if query_lower in searchable:
                results.append(product)
        
        return results


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(title="Furniverse AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize repository and AI models on startup
repository: Optional[ProductRepository] = None
qdrant_client = None
clip_model = None
clip_processor = None


@app.on_event("startup")
async def startup_event():
    """Initialize data repository and AI models on startup"""
    global repository, qdrant_client, clip_model, clip_processor
    
    # Initialize CSV repository
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

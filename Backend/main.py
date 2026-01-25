from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path


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


class RecommendRequest(BaseModel):
    query: str


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
            print(f"✓ Loaded {len(self.products)} products from CSV")
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
        
        # Update the colors list to include all variant colors
        for product in grouped.values():
            product.colors = [v.color for v in product.variants]
        
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

# Initialize repository on startup
repository: Optional[ProductRepository] = None


@app.on_event("startup")
async def startup_event():
    """Initialize data repository on startup"""
    global repository
    csv_path = Path(__file__).parent.parent / "Data" / "processed" / "products.csv"
    try:
        repository = CSVProductRepository(str(csv_path))
        print(f"✓ Repository initialized with {len(repository.get_all())} products")
    except Exception as e:
        print(f"✗ Failed to initialize repository: {e}")
        raise


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "Furniverse AI API is running",
        "products_loaded": len(repository.get_all()) if repository else 0
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


@app.post("/recommend")
def recommend(request: RecommendRequest):
    """
    Get product recommendations (placeholder for future AI/vector search)
    """
    if not repository:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    
    # Simple text search for now
    results = repository.search(request.query)
    
    if results:
        top_result = results[0]
        return {
            "recommended_product": str(top_result.id),
            "product_name": top_result.name,
            "explanation": f"Based on your query '{request.query}', we found this product. (Simple text search - AI vector search coming soon!)",
            "confidence": 0.75,
            "product": top_result
        }
    
    return {
        "recommended_product": None,
        "product_name": None,
        "explanation": f"No products found for '{request.query}'. Try different keywords!",
        "confidence": 0.0,
        "product": None
    }

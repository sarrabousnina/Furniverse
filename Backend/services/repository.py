"""
Product Repository - Data access layer for products
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
import pandas as pd
from .models import Product, Dimensions


# Category Mapping - CSV categories to Frontend categories
CATEGORY_MAP = {
    # Sofas
    "Three-seat sofas": "sofas",
    "Loveseats": "sofas",
    "Sectionals": "sofas",
    "Sofas with chaise lounge": "sofas",
    "Sectional sleeper sofas": "sofas",
    
    # Chairs
    "Dining chairs": "chairs",
    "Office chairs": "chairs",
    "Desk chairs for home": "chairs",
    "Upholstered chairs": "chairs",
    "Stools": "chairs",
    
    # Tables
    "Dining table sets for 4": "tables",
    "Dining table sets for 6": "tables",
    "Dining table sets for 10": "tables",
    "Small dining table sets for 2": "tables",
    "2 person dining tables": "tables",
    "Desks for home": "tables",
    "MITTZON office desks": "tables",
    
    # Beds
    "Bed frames": "beds",
    "Bed frames with storage": "beds",
    "Upholstered beds": "beds",
    "Twin beds & single beds": "beds",
    "Foam mattresses": "beds",
    "Spring & hybrid mattresses": "beds",
    
    # Storage
    "Storage shelves & shelving units": "storage",
    "Cube storage": "storage",
    "Cabinets, hutches & cupboards": "storage",
    "Kids boxes & baskets": "storage",
    "TROFAST combinations": "storage",
    "SMÅSTAD combinations": "storage",
    "Kids dressers & chest of drawers": "storage",
    "Toy boxes & shelves": "storage",
    
    # Bookcases
    "Bookshelves & bookcases": "bookcases",
    "Display shelves & picture ledges": "bookcases",
    
    # TV & Media
    "TV stands & benches": "tv-media",
    "TV & media storage": "tv-media",
    "BESTÅ TV benches": "tv-media",
    "BESTÅ frames": "tv-media",
    "BESTÅ sideboards": "tv-media",
    
    # Lighting
    "Pendant lighting": "lighting",
    "Table lamps": "lighting",
    "Desk lamps": "lighting",
    "Ceiling lamps": "lighting",
    "LED lamps": "lighting",
    "Lamp shades": "lighting",
    "LED strip lights": "lighting",
    
    # Textiles
    "Throw pillow covers": "textiles",
    "Pillow inserts": "textiles",
    "Accent & throw pillows": "textiles",
    
    # Decoration / Electronics
    "Cable management & cord organizers": "decoration",
    "Rechargeable batteries & battery chargers": "decoration",
    "Bluetooth speakers": "decoration",
    "Wireless chargers & accessories": "decoration",
    "USB chargers, portable chargers & more": "decoration",
    "Wooden toys": "decoration",
}


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
        """Search products"""
        pass


class CSVProductRepository(ProductRepository):
    """CSV-based product repository"""
    
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
        
        # Build dimensions object
        dimensions_dict = {}
        if pd.notna(row.get('width')) and row.get('width', 0) > 0:
            dimensions_dict['width'] = int(row['width'])
        if pd.notna(row.get('height')) and row.get('height', 0) > 0:
            dimensions_dict['height'] = int(row['height'])
        if pd.notna(row.get('depth')) and row.get('depth', 0) > 0:
            dimensions_dict['depth'] = int(row['depth'])
        
        # Split pipe-delimited strings
        images = row['images'].split('|') if pd.notna(row.get('images')) and row['images'] else [row['image']]
        features = row['features'].split('|') if pd.notna(row.get('features')) and row['features'] else []
        
        # Process styles
        styles_raw = row.get('styles', '')
        styles = [s.strip() for s in str(styles_raw).split(',') if s.strip()] if pd.notna(styles_raw) and styles_raw else []
        tags = row['tags'].split('|') if pd.notna(row.get('tags')) and row['tags'] else []
        
        # Process colors
        colors_raw = row.get('colors', '')
        colors = [c.strip() for c in str(colors_raw).split(',') if c.strip()] if pd.notna(colors_raw) and colors_raw else []
        
        # Map category
        raw_category = str(row['category']).strip()
        category = CATEGORY_MAP.get(raw_category, raw_category)
        
        # Boolean values
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
        """Get all products"""
        return self.products
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        for product in self.products:
            if product.id == product_id:
                return product
        return None
    
    def get_by_category(self, category: str) -> List[Product]:
        """Get products by category"""
        category_lower = category.lower()
        return [p for p in self.products if p.category.lower() == category_lower]
    
    def search(self, query: str) -> List[Product]:
        """Simple text search"""
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            searchable = f"{product.name} {product.description} {' '.join(product.tags)} {' '.join(product.styles)}".lower()
            if query_lower in searchable:
                results.append(product)
        
        return results

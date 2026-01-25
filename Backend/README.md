# Furniverse AI Backend

FastAPI backend serving furniture product data with clean, frontend-ready JSON responses.

## Features

✅ **CSV Data Source** - Loads 403 products from `data/dataset.csv`  
✅ **Frontend-Compatible API** - Returns exact product structure expected by React frontend  
✅ **Data Transformation** - Maps CSV columns to frontend schema with proper types  
✅ **Repository Pattern** - Easy to swap CSV for Qdrant vector DB later  
✅ **Category Mapping** - Converts IKEA categories to simplified frontend categories  
✅ **Auto-validation** - Pydantic models ensure data integrity

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start server (from Backend directory)
cd Backend
python -m uvicorn main:app --reload --port 8000
```

Server runs at: **http://127.0.0.1:8000**

## API Endpoints

### 📋 GET `/products`

Get all products (frontend-ready JSON)

**Query Parameters:**

- `category` (optional) - Filter by category: "Sofas", "Tables", "Lamps", "Chairs", "Beds", "Storage"
- `search` (optional) - Search by keywords

**Examples:**

```bash
GET /products                    # All products
GET /products?category=Sofas     # Only sofas
GET /products?search=modern      # Search for "modern"
```

### 🔍 GET `/products/{id}`

Get single product by ID

**Example:**

```bash
GET /products/40595942
```

### 📂 GET `/categories`

Get all available categories

**Response:**

```json
{
  "categories": ["Beds", "Chairs", "Lamps", "Sofas", "Storage", "Tables"]
}
```

### 🤖 POST `/recommend`

AI-powered recommendations (placeholder - simple search for now)

**Request:**

```json
{
  "query": "comfortable modern sofa"
}
```

### 📖 GET `/docs`

Interactive API documentation (Swagger UI)

## Product Schema

Each product has this exact structure (matches frontend):

```json
{
  "id": 40595942,
  "name": "GLOSTAD Sofa",
  "category": "Sofas",
  "price": 199,
  "rating": 3.9,
  "reviewCount": 40,
  "image": "https://...",
  "images": ["https://...", "https://..."],
  "description": "GLOSTAD Sofa - Knisa dark gray...",
  "features": ["GLOSTAD Sofa", "Removable cover", "Stationary cover"],
  "styles": ["Scandinavian", "Minimalist"],
  "colors": ["natural"],
  "tags": ["affordable", "comfortable", "minimalist"],
  "dimensions": {
    "width": 67,
    "height": 26,
    "depth": 30
  },
  "inStock": true,
  "trending": false
}
```

## Data Transformation

The backend handles these transformations automatically:

| CSV Format                               | Frontend Format        | Transformation            |
| ---------------------------------------- | ---------------------- | ------------------------- |
| Pipe-delimited strings `"a\|b\|c"`       | Arrays `["a","b","c"]` | Split by `\|`             |
| Single color `"blue"`                    | Array `["blue"]`       | Wrap in array             |
| String `"True"/"False"`                  | Boolean `true/false`   | Convert type              |
| Flat columns (width, height, depth)      | Nested object          | Build `dimensions` object |
| Detailed categories `"Three-seat sofas"` | Simple `"Sofas"`       | Map via `CATEGORY_MAP`    |
| Zero values `0`                          | Omitted                | Exclude from dimensions   |

## Architecture

```
main.py
├── Pydantic Models (Product, Dimensions)
├── Category Mapping (IKEA → Frontend)
├── Repository Pattern
│   ├── ProductRepository (Abstract)
│   └── CSVProductRepository (Implementation)
└── REST Endpoints (FastAPI)
```

**Why Repository Pattern?**

- Easy to swap data sources (CSV → Qdrant)
- No API changes needed when upgrading
- Frontend stays unchanged

## Future: Qdrant Integration

When ready to migrate from CSV to Qdrant:

1. Create `QdrantProductRepository` implementing `ProductRepository`
2. Swap `CSVProductRepository` → `QdrantProductRepository` in startup
3. API remains identical, frontend unchanged ✅

```python
# Future implementation
class QdrantProductRepository(ProductRepository):
    def search(self, query: str) -> List[Product]:
        # Vector search with embeddings
        embeddings = model.encode(query)
        results = qdrant_client.search(...)
        return [self._to_product(r) for r in results]
```

## Coming Soon

- 🔮 Vector embeddings for semantic search
- 🎯 AI-powered recommendations using Qdrant
- 🔍 Similarity search based on product features
- 📊 User preference tracking

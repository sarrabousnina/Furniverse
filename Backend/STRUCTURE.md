# Backend Folder Structure

## 📁 Organization

The Backend has been refactored into a clean, professional, and maintainable structure:

```
Backend/
├── main.py                    # 🚀 Thin API entrypoint (FastAPI application)
├── requirements.txt           # 📦 Python dependencies
├── README.md                  # 📖 This file
│
├── services/                  # 💼 Core Business Logic
│   ├── __init__.py
│   ├── models.py             # Pydantic data models
│   ├── repository.py         # Data access layer (CSV/Database)
│   ├── room_analysis.py      # AI room analysis service
│   ├── product_comparison.py # Product comparison engine
│   ├── embedding_tradeoff.py # CLIP-based trade-off system
│   ├── tripo_generator.py    # 3D model generation service
│   └── user_activity.py      # User activity tracking
│
├── analytics/                 # 📊 Analytics & Tracking
│   ├── __init__.py
│   └── search_analytics.py   # Real-time search analytics
│
├── config/                    # ⚙️ Configuration Files
│   ├── __init__.py
│   └── tradeoff_config.py    # Trade-off scenarios configuration
│
├── utils/                     # 🛠️ Utility Functions
│   ├── __init__.py
│   └── tradeoff_helpers.py   # Helper functions for trade-offs
│
├── tests/                     # 🧪 Tests & Experiments
│   ├── __init__.py
│   ├── test_blue_sofa.py
│   ├── test_comparison.py
│   ├── test_fusion.py
│   ├── test_recommendations.py
│   ├── test_smart_search.py
│   ├── test_smart_thresholds.py
│   ├── test_tradeoff_explanations.py
│   ├── test_tradeoff_trigger.py
│   ├── debug_candidates.py
│   └── demo_stats.py
│
├── assets/                    # 📦 Static Assets & Cache
│   └── 3d_model_cache.json   # Cached 3D models
│
└── temp_images/               # 🖼️ Temporary uploaded images
```

## 🎯 Key Principles

### 1. **Separation of Concerns**

- **API Layer** (`main.py`): Thin FastAPI application handling HTTP requests/responses
- **Business Logic** (`services/`): Core functionality and AI services
- **Data Access** (`services/repository.py`): Abstracted data layer
- **Configuration** (`config/`): Centralized settings
- **Utilities** (`utils/`): Reusable helper functions

### 2. **Clean main.py**

The main.py file is now a thin API entrypoint that:

- Defines FastAPI routes
- Imports from organized modules
- Minimal business logic (delegated to services/)
- Easy to understand and maintain

### 3. **Modular Services**

Each service has a single responsibility:

- `room_analysis.py`: AI-powered room analysis with furniture detection
- `product_comparison.py`: Side-by-side product comparisons
- `embedding_tradeoff.py`: Semantic trade-off calculations using CLIP
- `tripo_generator.py`: 3D model generation integration
- `user_activity.py`: User behavior tracking

### 4. **Type Safety**

- All models defined in `services/models.py`
- Pydantic for validation
- Clear type hints throughout

## 🚀 Running the Application

```bash
# From Backend directory
cd Backend

# Activate virtual environment (if using venv)
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

## 📝 Import Examples

```python
# In main.py
from services.models import Product, RecommendRequest
from services.repository import CSVProductRepository
from services.room_analysis import RoomAnalyzer
from utils.tradeoff_helpers import extract_user_preferences

# In services/
from .models import Product
from .repository import CSVProductRepository

# In tests/
import sys
sys.path.append('..')
from services.models import Product
```

## 🧪 Running Tests

```bash
# Run specific test
python tests/test_comparison.py

# Run all tests
python -m pytest tests/
```

## 🔄 Migration Notes

### Files Moved:

- ✅ Business logic → `services/`
- ✅ Test files → `tests/`
- ✅ Config files → `config/`
- ✅ Analytics → `analytics/`
- ✅ Static assets → `assets/`

### Import Updates:

- ✅ `main.py` imports from organized modules
- ✅ All cross-references updated
- ✅ `__init__.py` files created for clean imports

### Benefits:

- ✨ Easy to navigate and understand
- ✨ Scalable structure for growth
- ✨ Professional presentation-ready
- ✨ Clear separation of concerns
- ✨ Easier testing and maintenance

## 📚 Module Descriptions

### services/models.py

Pydantic models for:

- `Product`: Complete product data structure
- `Dimensions`: Product dimensions
- `ColorVariant`: Product color variants
- Request/Response models for API endpoints

### services/repository.py

Data access layer:

- `ProductRepository`: Abstract base class
- `CSVProductRepository`: CSV implementation
- `CATEGORY_MAP`: Category mappings

### services/room_analysis.py

AI-powered room analysis:

- Furniture detection using computer vision
- Missing furniture recommendations
- Room type classification

### services/product_comparison.py

Product comparison engine:

- Visual similarity using CLIP
- Price analysis
- Feature comparison
- AI recommendations

### services/embedding_tradeoff.py

Semantic trade-off system:

- CLIP-based preference extraction
- Trade-off calculation
- Explainable AI recommendations

## 🎨 Code Style

- Follow PEP 8
- Use type hints
- Clear docstrings
- Modular functions (single responsibility)
- Meaningful variable names

---

**Refactored on:** January 30, 2026
**Structure:** Clean, Professional, Maintainable ✨

# 🛋️ Furniverse

AI-powered furniture recommendation system using multimodal embeddings and vector search.

---

## 📝 Description

Furniverse is an intelligent furniture e-commerce platform that leverages advanced AI technologies to provide smarter product recommendations. Unlike traditional keyword-based search, our system understands the semantic meaning of queries, visual aesthetics, and style relationships between products.

**Key Features:**

- Semantic search using CLIP embeddings
- Budget-aware recommendations with smart fallbacks
- Graph-based product relationship discovery
- Color palette matching (548D color features)
- Multimodal fusion search (60% CLIP + 30% Graph + 10% Color)

---

## 🛠️ Tech Stack

### Backend

- **FastAPI** - Modern Python web framework
- **Qdrant Cloud** - Vector database for similarity search
- **CLIP** (OpenAI) - Multimodal text/image embeddings
- **Node2Vec** - Graph embeddings for product relationships
- **PyTorch** - Deep learning framework
- **Transformers** - Hugging Face model hub

### Frontend

- **React 18** - UI library
- **Vite** - Build tool
- **CSS Modules** - Component styling

### ML Pipeline

- **NetworkX** - Graph construction
- **scikit-learn** - Color clustering (K-means)
- **Pillow** - Image processing

---

## 🚀 Setup & Run Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/furniverse.git
cd furniverse
```

### 2. Install Dependencies

```bash
# Python dependencies
uv sync
# OR
pip install -r Pipeline/requirements.txt
pip install -r Backend/requirements.txt

# Frontend dependencies
cd Frontend
npm install
```

### 3. Configure Qdrant Cloud

Edit `Pipeline/qdrant_config.py`:

```python
QDRANT_URL = "your-qdrant-cluster-url"
QDRANT_API_KEY = "your-api-key"
```

### 4. Index Products (First Time Only)

```bash
cd Pipeline
python run_indexing.py
```

This generates CLIP embeddings, color features, and graph embeddings for ~200 products.

### 5. Start Backend API

```bash
cd Backend
uvicorn main:app --reload
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### 6. Start Frontend

```bash
cd Frontend
npm run dev
```

Frontend: `http://localhost:5173`

---

## 📡 API Usage

### Multimodal Fusion Search

```bash
curl -X POST "http://localhost:8000/recommend/fusion" \
  -H "Content-Type: application/json" \
  -d '{"query": "luxury velvet sofa under $400", "limit": 5}'
```

### Other Endpoints

- `POST /recommend/text` - CLIP semantic search
- `POST /recommend/similar/{id}` - Graph-based similar products
- `POST /recommend/smart` - Budget-aware search with fallback
- `GET /stats` - Database statistics

See full API documentation at `http://localhost:8000/docs`

---

## 👥 Team Members

- **[Marwa Mokhtar]**
- **[Roua Khalfet]**
- **[Sarra Bousnina]**
- **[Sameur Mkaouar]**
- **[Yassine Kharrat]**

---

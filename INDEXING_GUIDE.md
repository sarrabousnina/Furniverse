# Furniverse Indexing Pipeline Guide

Complete guide to indexing your products, users, and rooms into Qdrant for multimodal AI recommendations.

## 🎯 What Gets Indexed

### Products (Multimodal Features)
- ✅ **CLIP Text Embeddings** (512d) - Semantic text search
- ✅ **CLIP Image Embeddings** (512d) - Visual similarity search  
- ✅ **Color Palette Features** (548d) - RGB + HSV color-based filtering
- ✅ **Graph Embeddings** (256d) - Node2Vec for substitute discovery

### Users
- ✅ **Preference Vector** (512d) - Aggregated from purchase/interaction history
- ✅ **Graph Neighborhood** (256d) - Collaborative filtering patterns
- ✅ **Budget Patterns** - Min/max/avg prices, spending habits
- ✅ **Category/Style Preferences** - Favorite categories and styles

### Rooms
- ✅ **Room Profile** (512d) - Aggregated product embeddings
- ✅ **Color Palette** (548d) - Combined color scheme
- ✅ **Style Coherence** - Uniformity score for room aesthetics

---

## 🚀 Quick Start

### Prerequisites

1. **Install Qdrant** (Choose one):

   **Option A: Docker (Recommended)**
   ```powershell
   docker run -p 6333:6333 -p 6334:6334 -v ${PWD}/qdrant_storage:/qdrant/storage qdrant/qdrant
   ```

   **Option B: Local Installation**
   Download from: https://qdrant.tech/documentation/quick-start/

2. **Install Python Dependencies**
   ```powershell
   cd Pipeline
   pip install -r requirements.txt
   ```

---

## 📦 Step-by-Step Indexing

### Step 1: Index Products (Main Pipeline)

This is the **primary indexing script** that handles everything:

```powershell
cd Pipeline/indexing
python index_qdrant.py
```

**What it does:**
1. Builds product similarity graph
2. Computes Node2Vec graph embeddings (256d)
3. Generates CLIP text + image embeddings (512d each)
4. Extracts color palette features (RGB + HSV - 548d)
5. Indexes all features into Qdrant collection `products_multimodal`

**⚠️ Note:** By default, it indexes the first **200 products** for demo purposes. Edit `index_qdrant.py` line 323 to change:
```python
products_to_index = products[:200]  # Change number here
```

**Expected Output:**
```
✓ Loaded 403 products
✓ Connected to Qdrant at localhost:6333
✓ Created collection 'products_multimodal' with 4 vector types

[1/4] Building product graph and computing Node2Vec embeddings...
  ✓ Graph embeddings computed for 200 products

[2/4] Generating CLIP embeddings...
  ✓ Generated CLIP embeddings for 200 products

[3/4] Extracting color features...
  ✓ Extracted colors for 200 products

[4/4] Uploading to Qdrant...
  ✓ Indexed 200 products into Qdrant

✓ INDEXING COMPLETE!
```

---

### Step 2: Index Users (Optional)

Index user profiles with preference vectors and budget patterns:

```powershell
cd Pipeline/indexing
python index_profiles.py
```

**What it does:**
1. Builds user preference vectors from purchase/interaction history
2. Computes graph neighborhood embeddings
3. Extracts budget patterns (min/max/avg spending)
4. Indexes into Qdrant collection `users`

---

### Step 3: Build Product Graph Separately (Optional)

If you want to build the graph structure separately:

```powershell
cd Pipeline/graph
python build_graph.py
```

**What it creates:**
- `Data/processed/graphs/similarity_graph.gexf`
- `Data/processed/graphs/category_graph.gexf`
- `Data/processed/graphs/bipartite_graph.gexf`
- `Data/processed/graphs/full_graph.gexf`
- `Data/processed/graphs/node2vec_embeddings.json`

---

## 🔍 Verify Indexing

### Check Qdrant Collections

Visit: **http://localhost:6333/dashboard**

Or use Python:

```python
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)

# Check products collection
info = client.get_collection("products_multimodal")
print(f"Products indexed: {info.points_count}")
print(f"Vectors: {info.vectors_count}")

# Test search
results = client.search(
    collection_name="products_multimodal",
    query_vector=("text_clip", [0.1] * 512),  # Dummy vector
    limit=5
)
print(f"Sample results: {[r.payload['name'] for r in results]}")
```

---

## 🎨 Feature Details

### Color Palette Features (548 dimensions)

Extracted from product images:

- **Dominant Colors** (5 colors × 3 RGB = 15d)
- **Dominant Colors HSV** (5 colors × 3 HSV = 15d)
- **Average RGB** (3d)
- **Average HSV** (3d)
- **Color Histogram** (8×8×8 bins = 512d)

**Total:** 15 + 15 + 3 + 3 + 512 = **548 dimensions**

### Graph Embeddings (256 dimensions)

Node2Vec embeddings capturing:
- Product-to-product similarity
- Category/style relationships
- Price tier connections
- User-product bipartite relationships

---

## 🛠️ Customization

### Adjust Number of Products

Edit `Pipeline/indexing/index_qdrant.py`:

```python
# Line ~323
products_to_index = products[:200]  # Change to products (all) or products[:N]
```

### Change Color Palette Size

Edit `Pipeline/indexing/index_qdrant.py`:

```python
# Line ~60
self.color_extractor = ColorExtractor(n_colors=5)  # Change n_colors
```

### Adjust Graph Parameters

Edit `Pipeline/indexing/index_qdrant.py`:

```python
# Line ~139 (in index_products method)
graph_embeddings = self.graph_builder.compute_node2vec_embeddings(
    dimensions=256,      # Change embedding size
    walk_length=30,      # Change random walk length
    num_walks=200        # Change number of walks
)
```

---

## 📊 Collection Schemas

### products_multimodal

**Vectors:**
- `text_clip`: 512d CLIP text embedding
- `image_clip`: 512d CLIP image embedding
- `color`: 548d color palette features
- `graph`: 256d Node2Vec graph embedding

**Payload:**
```json
{
  "product_id": "12345",
  "name": "GLOSTAD Sofa",
  "category": "Three-seat sofas",
  "price": 199,
  "rating": 3.9,
  "styles": ["Scandinavian", "Minimalist"],
  "colors": ["dark gray"],
  "color_palette": {
    "dominant_colors_rgb": [[45, 45, 50], ...],
    "color_names": ["gray", "black", ...]
  }
}
```

### users

**Vectors:**
- `preference`: 512d preference vector
- `graph_neighborhood`: 256d graph neighborhood

**Payload:**
```json
{
  "user_id": "user_0001",
  "budget_avg": 250,
  "budget_min": 10,
  "budget_max": 1200,
  "num_purchases": 15,
  "favorite_categories": {"Sofas": 5, "Tables": 3}
}
```

---

## 🔧 Troubleshooting

### Qdrant Connection Error

```
Failed to connect to Qdrant at localhost:6333
```

**Solution:** Make sure Qdrant is running:
```powershell
docker ps  # Check if Qdrant container is running
# Or restart Qdrant
docker run -p 6333:6333 qdrant/qdrant
```

### Out of Memory

```
RuntimeError: CUDA out of memory
```

**Solution:** Reduce batch size or number of products:
```python
# Edit index_qdrant.py
products_to_index = products[:50]  # Smaller batch
```

### Missing Dependencies

```
ModuleNotFoundError: No module named 'node2vec'
```

**Solution:**
```powershell
pip install node2vec networkx
```

---

## ✅ Next Steps

After indexing:

1. **Test Search Queries**
   - Text search: "modern leather sofa under $500"
   - Image search: Upload sofa image, find similar
   - Color search: Find products with specific color palette
   
2. **Build Recommendation API**
   - Update Backend API with Qdrant search
   - Implement budget-aware recommendations
   - Add substitute product discovery

3. **Frontend Integration**
   - Connect search to Qdrant
   - Display multimodal results
   - Show color palettes and style suggestions

---

## 📚 Architecture Summary

```
Pipeline/
├── embeddings/
│   ├── engine.py          # Main embedding orchestrator
│   ├── models.py          # CLIP, SBERT, Graph models
│   ├── storage.py         # Qdrant storage interface
│   └── color_extractor.py # RGB + HSV color features
├── graph/
│   └── build_graph.py     # Product graph + Node2Vec
├── indexing/
│   ├── index_qdrant.py    # ⭐ MAIN INDEXING SCRIPT
│   └── index_profiles.py  # User + Room indexing
```

**Run Order:**
1. `index_qdrant.py` → Index products with all features
2. `index_profiles.py` → (Optional) Index users and rooms

---

## 🎯 Hackathon Tips

For your hackathon demo:

1. **Index 100-200 products** (faster, still impressive)
2. **Focus on multimodal search** (text + image + color)
3. **Demo budget-aware recommendations** ("Italian leather sofa under $400")
4. **Show substitute discovery** (graph embeddings finding similar but cheaper)
5. **Highlight color palette matching** (find products matching room colors)

Good luck! 🚀

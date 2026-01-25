# 🎯 Furniverse Complete Indexing Pipeline - Summary

## ✅ What Was Created

### 1. **Color Palette Extraction** (`Pipeline/embeddings/color_extractor.py`)

- Extracts dominant colors from product images
- Generates RGB + HSV features (548 dimensions total)
- Supports K-means clustering for color palette detection
- Provides human-readable color names

**Key Features:**

- 5 dominant colors (RGB + HSV = 30d)
- Average color (RGB + HSV = 6d)
- Color histogram (8×8×8 bins = 512d)
- **Total: 548 dimensions**

---

### 2. **Product Graph Builder** (`Pipeline/graph/build_graph.py`)

- Builds multiple graph types:
  - Similarity graph (embedding-based)
  - Category/style graph (attribute-based)
  - Price tier graph (budget-based)
  - Bipartite user-product graph (collaborative filtering)
- Computes Node2Vec embeddings (256d)
- Saves graphs in GEXF format

**Key Features:**

- Multi-relational graph structure
- Node2Vec random walks for embeddings
- Configurable k-neighbors and similarity thresholds

---

### 3. **Main Product Indexer** (`Pipeline/indexing/index_qdrant.py`)

- **Primary indexing script** - orchestrates everything
- Combines 4 types of embeddings:
  1. CLIP text embeddings (512d)
  2. CLIP image embeddings (512d)
  3. Color palette features (548d)
  4. Graph embeddings (256d)
- Creates Qdrant collection with named vectors
- Handles batch processing and error recovery

**Usage:**

```powershell
cd Pipeline/indexing
python index_qdrant.py
```

---

### 4. **User & Room Profile Indexer** (`Pipeline/indexing/index_profiles.py`)

- Creates user profiles:
  - Preference vectors from purchase history
  - Graph neighborhood embeddings
  - Budget patterns (min/max/avg)
  - Category/style preferences
- Creates room profiles:
  - Aggregated product embeddings
  - Combined color palettes
  - Style coherence scores

**Usage:**

```powershell
cd Pipeline/indexing
python index_profiles.py
```

---

### 5. **Quick Setup Script** (`Pipeline/run_indexing.py`)

- Interactive setup wizard
- Checks Qdrant connection
- Installs dependencies
- Runs complete indexing pipeline
- Verifies results

**Usage:**

```powershell
cd Pipeline
python run_indexing.py
```

---

### 6. **Updated Dependencies**

- `pyproject.toml` - Project dependencies
- `Pipeline/requirements.txt` - Detailed requirements
- Added: torch, transformers, node2vec, networkx

---

## 📊 Qdrant Collections Schema

### `products_multimodal`

```
Vectors:
  - text_clip: 512d (CLIP text embedding)
  - image_clip: 512d (CLIP image embedding)
  - color: 548d (RGB + HSV features)
  - graph: 256d (Node2Vec embedding)

Payload:
  - product_id, name, category, price, rating
  - styles[], colors[], tags[]
  - color_palette{dominant_colors_rgb, color_names}
  - image, primary_image
```

### `users`

```
Vectors:
  - preference: 512d (aggregated CLIP from purchases)
  - graph_neighborhood: 256d (collaborative patterns)

Payload:
  - user_id, budget_avg, budget_min, budget_max
  - num_purchases, num_interactions
  - favorite_categories{}
```

### `rooms`

```
Vectors:
  - room_profile: 512d (aggregated product embeddings)
  - color_palette: 548d (combined room colors)

Payload:
  - room_id, room_name, num_products
  - total_price, avg_price
  - styles{}, dominant_style, style_coherence
```

---

## 🚀 How to Use

### Option 1: Quick Start (Automated)

```powershell
cd Pipeline
python run_indexing.py
```

Follow the interactive prompts.

### Option 2: Manual Step-by-Step

**1. Start Qdrant:**

```powershell
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

**2. Install dependencies:**

```powershell
cd Pipeline
pip install -r requirements.txt
```

**3. Index products:**

```powershell
cd indexing
python index_qdrant.py
```

**4. Index profiles (optional):**

```powershell
python index_profiles.py
```

**5. Verify:**
Visit http://localhost:6333/dashboard

---

## 🎨 Multimodal Search Examples

### 1. Text Search (CLIP Text)

```python
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)

# Generate text embedding
from transformers import CLIPModel, CLIPProcessor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

query = "modern leather sofa under $500"
inputs = processor(text=[query], return_tensors="pt", padding=True)
text_embedding = model.get_text_features(**inputs).detach().numpy()[0]

# Search
results = client.search(
    collection_name="products_multimodal",
    query_vector=("text_clip", text_embedding.tolist()),
    limit=10,
    query_filter={
        "must": [
            {"key": "price", "range": {"lte": 500}}
        ]
    }
)

for result in results:
    print(f"{result.payload['name']} - ${result.payload['price']}")
```

### 2. Image Search (CLIP Image)

```python
# Upload user's sofa image, find similar
image_path = "user_sofa.jpg"

from PIL import Image
img = Image.open(image_path)
inputs = processor(images=img, return_tensors="pt")
image_embedding = model.get_image_features(**inputs).detach().numpy()[0]

results = client.search(
    collection_name="products_multimodal",
    query_vector=("image_clip", image_embedding.tolist()),
    limit=10
)
```

### 3. Color-Based Search

```python
# Find products with similar color palette
results = client.search(
    collection_name="products_multimodal",
    query_vector=("color", target_color_vector),
    limit=10
)
```

### 4. Graph-Based Substitutes

```python
# Find similar products in the graph (substitutes)
results = client.search(
    collection_name="products_multimodal",
    query_vector=("graph", product_graph_embedding),
    limit=10
)
```

---

## 🎯 Hackathon Use Cases

### Use Case 1: Budget-Aware Recommendations

**Query:** "I want an Italian leather sofa for $400"

**Pipeline:**

1. Search with text_clip: "Italian leather sofa"
2. Filter by price: ≤ $400
3. If no results, search with graph: Find substitutes (fabric instead of leather)
4. Return: "No Italian leather sofas at $400, but here are similar fabric sofas in your budget"

### Use Case 2: Room Matching

**Query:** "Find products that match my living room"

**Pipeline:**

1. User uploads room image
2. Extract room color palette
3. Search with color vector
4. Filter by compatible styles
5. Return: Products that match room aesthetics

### Use Case 3: Visual Discovery

**Query:** Upload image of liked product

**Pipeline:**

1. Extract CLIP image embedding
2. Search products_multimodal with image_clip
3. Find visually similar products
4. Optionally filter by price range

---

## 🔧 Customization Guide

### Change Number of Products Indexed

Edit `Pipeline/indexing/index_qdrant.py` line ~323:

```python
products_to_index = products[:200]  # Change to desired number
```

### Adjust Color Palette Size

Edit `Pipeline/embeddings/color_extractor.py`:

```python
extractor = ColorExtractor(n_colors=5)  # Change n_colors
```

### Modify Graph Parameters

Edit `Pipeline/graph/build_graph.py`:

```python
builder.build_similarity_graph(
    products,
    embeddings,
    k_neighbors=10,              # Number of neighbors
    similarity_threshold=0.7      # Minimum similarity
)
```

### Change Node2Vec Dimensions

Edit `Pipeline/indexing/index_qdrant.py` line ~139:

```python
graph_embeddings = self.graph_builder.compute_node2vec_embeddings(
    dimensions=256,       # Embedding dimension
    walk_length=30,       # Random walk length
    num_walks=200         # Number of walks per node
)
```

---

## 📈 Performance Tips

### For Faster Indexing:

1. **Reduce products**: Index 50-100 products for testing
2. **Disable features**: Set `use_graph=False` or `use_colors=False`
3. **Use GPU**: CLIP will auto-detect and use CUDA if available
4. **Batch processing**: Increase batch_size in index_products()

### For Better Quality:

1. **More Node2Vec walks**: Increase num_walks to 300-500
2. **Higher k-neighbors**: Increase k_neighbors to 15-20
3. **More color clusters**: Increase n_colors to 7-10

---

## 🐛 Troubleshooting

| Issue                 | Solution                                              |
| --------------------- | ----------------------------------------------------- |
| Qdrant not connecting | Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant` |
| Out of memory         | Reduce products or batch_size                         |
| Missing transformers  | `pip install transformers torch`                      |
| Missing node2vec      | `pip install node2vec networkx`                       |
| Slow indexing         | Use GPU, reduce products, or disable graph            |

---

## ✨ What Makes This Unique

1. **True Multimodality**: Combines text, image, color, and graph in one search
2. **Budget-Aware**: Built-in price filtering and substitute discovery
3. **Color Intelligence**: RGB + HSV features for aesthetic matching
4. **Graph Relationships**: Discovers substitutes via product graph
5. **Hackathon-Ready**: Complete pipeline in runnable scripts

---

## 📚 Files Created

```
Pipeline/
├── embeddings/
│   └── color_extractor.py     ✅ NEW - RGB/HSV color extraction
├── graph/
│   └── build_graph.py          ✅ UPDATED - Product graph + Node2Vec
├── indexing/
│   ├── index_qdrant.py         ✅ NEW - Main indexing pipeline
│   └── index_profiles.py       ✅ NEW - User/room profiles
├── requirements.txt            ✅ NEW - Dependencies
└── run_indexing.py             ✅ NEW - Quick setup script

Project Root/
├── INDEXING_GUIDE.md           ✅ NEW - Comprehensive guide
└── pyproject.toml              ✅ UPDATED - Added dependencies
```

---

## 🎉 You're Ready!

Your Furniverse indexing pipeline is complete and ready for your hackathon demo!

**Next Steps:**

1. Start Qdrant
2. Run `python Pipeline/run_indexing.py`
3. Build recommendation API
4. Demo multimodal search!

Good luck with your hackathon! 🚀

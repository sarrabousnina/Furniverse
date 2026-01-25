"""
Product Graph Builder for Furniverse

Builds multiple types of graphs for the recommendation system:
1. Product Similarity Graph - connects products with similar features
2. Category/Style Graph - connects products in same categories/styles
3. Price Tier Graph - connects products in similar price ranges
4. Bipartite User-Product Graph - for collaborative filtering

These graphs enable:
- Node2Vec embeddings for graph-based recommendations
- Discovery of substitute products
- Budget-aware pattern detection
- Neighborhood-based recommendations
"""

import json
import numpy as np
import networkx as nx
from typing import List, Dict, Any, Tuple
from pathlib import Path
from collections import defaultdict


class ProductGraphBuilder:
    """Build various graph structures for product recommendations"""
    
    def __init__(self):
        self.similarity_graph = nx.Graph()
        self.category_graph = nx.Graph()
        self.bipartite_graph = nx.Graph()
        self.full_graph = nx.Graph()  # Combined graph
    
    def build_similarity_graph(self, products: List[Dict], 
                               embeddings: np.ndarray, 
                               k_neighbors: int = 10,
                               similarity_threshold: float = 0.7) -> nx.Graph:
        """
        Build product similarity graph based on embeddings.
        
        Args:
            products: List of product dictionaries
            embeddings: Product embeddings (n_products, embedding_dim)
            k_neighbors: Number of nearest neighbors to connect
            similarity_threshold: Minimum cosine similarity to create edge
        
        Returns:
            NetworkX graph with similarity edges
        """
        print(f"Building similarity graph for {len(products)} products...")
        
        # Normalize embeddings for cosine similarity
        embeddings_norm = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-7)
        
        # Compute similarity matrix
        similarity_matrix = embeddings_norm @ embeddings_norm.T
        
        # Add nodes with attributes
        for idx, product in enumerate(products):
            self.similarity_graph.add_node(
                str(product['id']),
                name=product['name'],
                category=product.get('category'),
                price=product.get('price'),
                styles=product.get('styles', []),
                colors=product.get('colors', [])
            )
        
        # Add edges based on similarity
        for idx, product in enumerate(products):
            # Get k most similar products
            similarities = similarity_matrix[idx]
            top_indices = np.argsort(similarities)[::-1][1:k_neighbors+1]  # Exclude self
            
            for neighbor_idx in top_indices:
                sim_score = similarities[neighbor_idx]
                
                if sim_score >= similarity_threshold:
                    self.similarity_graph.add_edge(
                        str(product['id']),
                        str(products[neighbor_idx]['id']),
                        weight=float(sim_score),
                        edge_type='similarity'
                    )
        
        print(f"✓ Similarity graph: {self.similarity_graph.number_of_nodes()} nodes, "
              f"{self.similarity_graph.number_of_edges()} edges")
        
        return self.similarity_graph
    
    def build_category_graph(self, products: List[Dict]) -> nx.Graph:
        """
        Build category/style/color graph connecting products with shared attributes.
        
        Args:
            products: List of product dictionaries
        
        Returns:
            NetworkX graph with attribute-based edges
        """
        print(f"Building category graph...")
        
        # Group products by attributes
        category_groups = defaultdict(list)
        style_groups = defaultdict(list)
        color_groups = defaultdict(list)
        
        for product in products:
            pid = str(product['id'])
            
            # Add node
            self.category_graph.add_node(
                pid,
                name=product['name'],
                category=product.get('category'),
                price=product.get('price')
            )
            
            # Group by category
            if product.get('category'):
                category_groups[product['category']].append(pid)
            
            # Group by styles
            for style in product.get('styles', []):
                style_groups[style].append(pid)
            
            # Group by colors
            for color in product.get('colors', []):
                color_groups[color].append(pid)
        
        # Create edges within each group
        def connect_group(group_dict: Dict, edge_type: str):
            for group_name, product_ids in group_dict.items():
                if len(product_ids) < 2:
                    continue
                
                # Connect all products in the group (clique)
                for i, pid1 in enumerate(product_ids):
                    for pid2 in product_ids[i+1:]:
                        if not self.category_graph.has_edge(pid1, pid2):
                            self.category_graph.add_edge(
                                pid1, pid2,
                                edge_type=edge_type,
                                attribute=group_name,
                                weight=1.0
                            )
                        else:
                            # Increase weight if already connected
                            self.category_graph[pid1][pid2]['weight'] += 0.5
        
        connect_group(category_groups, 'category')
        connect_group(style_groups, 'style')
        connect_group(color_groups, 'color')
        
        print(f"✓ Category graph: {self.category_graph.number_of_nodes()} nodes, "
              f"{self.category_graph.number_of_edges()} edges")
        
        return self.category_graph
    
    def build_price_tier_graph(self, products: List[Dict], 
                               tier_ranges: List[Tuple[int, int]] = None) -> nx.Graph:
        """
        Build price tier graph connecting products in similar price ranges.
        
        Args:
            products: List of product dictionaries
            tier_ranges: List of (min, max) price ranges
        
        Returns:
            NetworkX graph with price-based edges
        """
        if tier_ranges is None:
            # Default price tiers
            tier_ranges = [
                (0, 50),      # Budget
                (50, 150),    # Low-mid
                (150, 300),   # Mid
                (300, 600),   # High-mid
                (600, 10000)  # Premium
            ]
        
        price_graph = nx.Graph()
        tier_groups = defaultdict(list)
        
        # Assign products to price tiers
        for product in products:
            pid = str(product['id'])
            price = product.get('price', 0)
            
            price_graph.add_node(pid, price=price)
            
            for tier_idx, (min_price, max_price) in enumerate(tier_ranges):
                if min_price <= price < max_price:
                    tier_groups[tier_idx].append(pid)
                    break
        
        # Connect products in same tier
        for tier_idx, product_ids in tier_groups.items():
            for i, pid1 in enumerate(product_ids):
                for pid2 in product_ids[i+1:]:
                    price_graph.add_edge(
                        pid1, pid2,
                        edge_type='price_tier',
                        tier=tier_idx,
                        weight=0.5
                    )
        
        return price_graph
    
    def build_bipartite_graph(self, products: List[Dict],
                             users: List[Dict] = None,
                             purchases: List[Dict] = None,
                             interactions: List[Dict] = None) -> nx.Graph:
        """
        Build bipartite user-product graph for collaborative filtering.
        
        Args:
            products: List of product dictionaries
            users: List of user dictionaries
            purchases: List of purchase records
            interactions: List of interaction records
        
        Returns:
            NetworkX bipartite graph
        """
        print(f"Building bipartite user-product graph...")
        
        # Add product nodes
        for product in products:
            self.bipartite_graph.add_node(
                f"prod_{product['id']}",
                bipartite=0,  # Product side
                node_type='product',
                name=product['name'],
                price=product.get('price')
            )
        
        # Add user nodes and edges if data available
        if users:
            for user in users:
                self.bipartite_graph.add_node(
                    user['user_id'],
                    bipartite=1,  # User side
                    node_type='user'
                )
        
        # Add purchase edges
        if purchases:
            for purchase in purchases:
                self.bipartite_graph.add_edge(
                    purchase['user_id'],
                    f"prod_{purchase['product_id']}",
                    edge_type='purchase',
                    price_paid=purchase.get('price_paid'),
                    date=purchase.get('purchase_date'),
                    weight=2.0  # Purchases weighted higher
                )
        
        # Add interaction edges
        if interactions:
            for interaction in interactions:
                if self.bipartite_graph.has_edge(
                    interaction['user_id'],
                    f"prod_{interaction['product_id']}"
                ):
                    # Already has purchase edge, skip
                    continue
                
                self.bipartite_graph.add_edge(
                    interaction['user_id'],
                    f"prod_{interaction['product_id']}",
                    edge_type='interaction',
                    action=interaction.get('action'),
                    weight=1.0
                )
        
        print(f"✓ Bipartite graph: {self.bipartite_graph.number_of_nodes()} nodes, "
              f"{self.bipartite_graph.number_of_edges()} edges")
        
        return self.bipartite_graph
    
    def build_combined_graph(self) -> nx.Graph:
        """
        Combine all graphs into a single multi-relational graph.
        
        Returns:
            Combined NetworkX graph
        """
        print("Building combined multi-relational graph...")
        
        # Start with similarity graph
        self.full_graph = self.similarity_graph.copy()
        
        # Add category edges
        for u, v, data in self.category_graph.edges(data=True):
            if self.full_graph.has_edge(u, v):
                # Combine weights
                self.full_graph[u][v]['weight'] += data.get('weight', 1.0) * 0.5
                self.full_graph[u][v]['edge_types'] = self.full_graph[u][v].get('edge_types', []) + [data.get('edge_type')]
            else:
                self.full_graph.add_edge(u, v, **data)
        
        print(f"✓ Combined graph: {self.full_graph.number_of_nodes()} nodes, "
              f"{self.full_graph.number_of_edges()} edges")
        
        return self.full_graph
    
    def save_graphs(self, output_dir: Path):
        """
        Save all graphs to disk.
        
        Args:
            output_dir: Directory to save graphs
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        graphs = {
            'similarity_graph.gexf': self.similarity_graph,
            'category_graph.gexf': self.category_graph,
            'bipartite_graph.gexf': self.bipartite_graph,
            'full_graph.gexf': self.full_graph
        }
        
        for filename, graph in graphs.items():
            if graph.number_of_nodes() > 0:
                path = output_dir / filename
                nx.write_gexf(graph, path)
                print(f"✓ Saved {filename}")
    
    def compute_node2vec_embeddings(self, graph: nx.Graph = None, 
                                   dimensions: int = 256,
                                   walk_length: int = 30,
                                   num_walks: int = 200) -> Dict[str, np.ndarray]:
        """
        Compute Node2Vec embeddings for a graph.
        
        Args:
            graph: NetworkX graph (uses full_graph if None)
            dimensions: Embedding dimension
            walk_length: Length of random walks
            num_walks: Number of walks per node
        
        Returns:
            Dictionary mapping node_id -> embedding vector
        """
        if graph is None:
            graph = self.full_graph
        
        if graph.number_of_nodes() == 0:
            print("⚠ Empty graph, cannot compute embeddings")
            return {}
        
        print(f"Computing Node2Vec embeddings ({dimensions}d)...")
        
        try:
            from node2vec import Node2Vec
            
            # Create Node2Vec model
            node2vec = Node2Vec(
                graph,
                dimensions=dimensions,
                walk_length=walk_length,
                num_walks=num_walks,
                workers=4,
                quiet=False
            )
            
            # Fit model
            model = node2vec.fit(window=10, min_count=1, batch_words=4)
            
            # Extract embeddings
            embeddings = {}
            for node in graph.nodes():
                embeddings[str(node)] = model.wv[str(node)]
            
            print(f"✓ Computed embeddings for {len(embeddings)} nodes")
            return embeddings
            
        except ImportError:
            print("⚠ node2vec not installed. Run: pip install node2vec")
            return {}


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Build all product graphs from processed data"""
    
    print("="*80)
    print("FURNIVERSE PRODUCT GRAPH BUILDER")
    print("="*80)
    
    # Load data
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'Data' / 'processed'
    
    with open(data_dir / 'products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"✓ Loaded {len(products)} products")
    
    # Load user data if available
    users, purchases, interactions = None, None, None
    
    try:
        with open(data_dir / 'users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        print(f"✓ Loaded {len(users)} users")
    except FileNotFoundError:
        print("⚠ users.json not found, skipping user nodes")
    
    try:
        with open(data_dir / 'purchases.json', 'r', encoding='utf-8') as f:
            purchases = json.load(f)
        print(f"✓ Loaded {len(purchases)} purchases")
    except FileNotFoundError:
        print("⚠ purchases.json not found, skipping purchase edges")
    
    try:
        with open(data_dir / 'interactions.json', 'r', encoding='utf-8') as f:
            interactions = json.load(f)
        print(f"✓ Loaded {len(interactions)} interactions")
    except FileNotFoundError:
        print("⚠ interactions.json not found, skipping interaction edges")
    
    # Build graphs
    builder = ProductGraphBuilder()
    
    # For embeddings, load or create simple features
    print("\nGenerating product embeddings for graph building...")
    embeddings = np.array([u['centroid'] if 'centroid' in u else np.random.randn(384) 
                          for u in users[:len(products)]]) if users else np.random.randn(len(products), 384)
    
    # Build individual graphs
    print("\n" + "="*80)
    builder.build_similarity_graph(products, embeddings, k_neighbors=10)
    builder.build_category_graph(products)
    builder.build_bipartite_graph(products, users, purchases, interactions)
    builder.build_combined_graph()
    
    # Save graphs
    print("\n" + "="*80)
    output_dir = project_root / 'Data' / 'processed' / 'graphs'
    builder.save_graphs(output_dir)
    
    # Compute Node2Vec embeddings
    print("\n" + "="*80)
    graph_embeddings = builder.compute_node2vec_embeddings(
        builder.full_graph,
        dimensions=256,
        walk_length=30,
        num_walks=200
    )
    
    # Save embeddings
    if graph_embeddings:
        embeddings_path = output_dir / 'node2vec_embeddings.json'
        # Convert numpy arrays to lists for JSON serialization
        embeddings_serializable = {k: v.tolist() for k, v in graph_embeddings.items()}
        with open(embeddings_path, 'w') as f:
            json.dump(embeddings_serializable, f)
        print(f"✓ Saved Node2Vec embeddings to {embeddings_path}")
    
    print("\n" + "="*80)
    print("✓ GRAPH BUILDING COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()

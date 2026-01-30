"""
Embedding-based trade-off system using CLIP for semantic understanding
Instead of hardcoded rules, uses semantic similarity
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from transformers import CLIPProcessor, CLIPModel


class EmbeddingAttributeExtractor:
    """
    Extract user preferences using CLIP embeddings for semantic understanding
    instead of hardcoded keyword matching
    """

    def __init__(self, clip_model, clip_processor):
        self.clip_model = clip_model
        self.clip_processor = clip_processor

        # Pre-compute embeddings for common attributes
        self.attribute_embeddings = self._build_attribute_embeddings()

        # Build concept hierarchy
        self.concepts = self._build_concepts()

    def _build_attribute_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Build embeddings for common attributes using CLIP

        Returns:
            Dict mapping attribute names to their embeddings
        """
        attributes = {
            # Materials
            "leather": "genuine leather material",
            "pu leather": "faux leather synthetic material",
            "velvet": "velvet fabric plush material",
            "fabric": "fabric cloth material",
            "wood": "solid wood natural material",
            "metal": "metal steel material",

            # Styles
            "modern": "modern contemporary sleek style",
            "traditional": "traditional classic vintage style",
            "industrial": "industrial urban metal style",
            "minimalist": "minimalist simple clean style",
            "scandinavian": "scandinavian nordic light wood style",

            # Colors
            "red": "red color crimson",
            "blue": "blue color navy azure",
            "green": "green color emerald sage",
            "neutral": "neutral color beige gray white black",

            # Comfort
            "comfy": "comfortable plush soft cushioned",
            "firm": "firm supportive seat",

            # Budget-related
            "affordable": "affordable cheap budget low price",
            "premium": "premium expensive luxury high price"
        }

        embeddings = {}
        for attr_name, description in attributes.items():
            inputs = self.clip_processor(
                text=[description],
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            features = self.clip_model.get_text_features(**inputs)
            embeddings[attr_name] = features.detach().numpy()[0]

        return embeddings

    def _build_concepts(self) -> Dict[str, Dict]:
        """
        Build concept relationships for explainability

        Uses semantic distances between embeddings
        """
        return {
            "material": {
                "leather": {
                    "alternatives": ["pu leather", "velvet", "fabric"],
                    "upgrade": "genuine leather",
                    "description": "durable luxurious material"
                },
                "wood": {
                    "alternatives": ["metal", "glass"],
                    "description": "natural solid material"
                }
            },
            "style": {
                "modern": {
                    "opposites": ["traditional", "vintage"],
                    "related": ["minimalist", "contemporary", "scandinavian"],
                    "description": "sleek contemporary style"
                },
                "traditional": {
                    "opposites": ["modern", "minimalist"],
                    "related": ["vintage", "classic"],
                    "description": "classic timeless style"
                }
            },
            "budget": {
                "affordable": {
                    "range": (0, 500),
                    "description": "budget-friendly price"
                },
                "mid_range": {
                    "range": (500, 1500),
                    "description": "moderate price"
                },
                "premium": {
                    "range": (1500, 10000),
                    "description": "luxury high-end price"
                }
            }
        }

    def extract_preferences(self, query: str, query_embedding: np.ndarray) -> Dict[str, any]:
        """
        Extract preferences from query using semantic similarity

        Args:
            query: User's natural language query
            query_embedding: CLIP embedding of the query

        Returns:
            Dict with extracted preferences and confidence scores
        """
        preferences = {
            "budget": None,
            "material": None,
            "style": None,
            "color": None,
            "comfort": None,
            "confidences": {}  # Track how confident we are
        }

        # Material detection using similarity (hierarchical approach)
        # Only base materials - variants checked separately
        material_scores = {}
        for material in ["leather", "velvet", "fabric", "wood", "metal"]:
            similarity = self._cosine_similarity(
                query_embedding,
                self.attribute_embeddings[material]
            )
            material_scores[material] = similarity

        # Get top material if above threshold
        if material_scores:
            top_material = max(material_scores, key=material_scores.get)
            if material_scores[top_material] > 0.3:  # Threshold
                preferences["material"] = top_material
                preferences["confidences"]["material"] = float(material_scores[top_material])

                # If leather detected, check for specific variant
                if top_material == "leather":
                    # Check which type of leather (genuine vs PU vs faux)
                    leather_variants = ["pu leather", "genuine leather", "faux leather"]
                    variant_scores = {}

                    for variant in leather_variants:
                        if variant in self.attribute_embeddings:
                            variant_similarity = self._cosine_similarity(
                                query_embedding,
                                self.attribute_embeddings[variant]
                            )
                            variant_scores[variant] = variant_similarity

                    # If a variant has higher similarity, use it
                    if variant_scores:
                        top_variant = max(variant_scores, key=variant_scores.get)
                        # Only use variant if it's significantly better (not just slightly higher)
                        # This prevents "pu leather" from winning when user just said "leather"
                        base_score = material_scores["leather"]
                        variant_score = variant_scores[top_variant]

                        # Only override if variant is explicitly mentioned (much higher similarity)
                        if variant_score > base_score + 0.1:  # Significant boost
                            preferences["material"] = top_variant
                            preferences["confidences"]["material"] = float(variant_score)
                            preferences["base_material"] = "leather"  # Track the base

        # Style detection using similarity
        style_scores = {}
        for style in ["modern", "traditional", "industrial", "minimalist", "scandinavian"]:
            similarity = self._cosine_similarity(
                query_embedding,
                self.attribute_embeddings[style]
            )
            style_scores[style] = similarity

        if style_scores:
            top_style = max(style_scores, key=style_scores.get)
            if style_scores[top_style] > 0.3:
                preferences["style"] = top_style
                preferences["confidences"]["style"] = float(style_scores[top_style])

        # Comfort detection
        comfort_similarity = self._cosine_similarity(
            query_embedding,
            self.attribute_embeddings["comfy"]
        )
        if comfort_similarity > 0.3:
            preferences["comfort"] = "high"
            preferences["confidences"]["comfort"] = float(comfort_similarity)

        # Budget extraction (regex still most reliable for numbers)
        import re
        budget_patterns = [
            r'under\s+\$?(\d+)',
            r'budget\s+(?:of\s+)?\$?(\d+)',
            r'cheap(?:est)?\s+(?:under\s+)?\$?(\d+)',
        ]
        query_lower = query.lower()
        for pattern in budget_patterns:
            match = re.search(pattern, query_lower)
            if match:
                budget_str = match.group(1)
                if budget_str and budget_str.isdigit():
                    preferences["budget"] = float(budget_str)
                    break

        return preferences

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2) if norm1 and norm2 else 0


class EmbeddingTradeoffAnalyzer:
    """
    Analyze trade-offs using semantic similarity between user query and products
    Provides explainability based on embedding distances
    """

    def __init__(self, clip_model, clip_processor, extractor: EmbeddingAttributeExtractor):
        self.clip_model = clip_model
        self.clip_processor = clip_processor
        self.extractor = extractor

    def analyze_tradeoffs(
        self,
        product: dict,
        preferences: dict,
        query_embedding: np.ndarray
    ) -> dict:
        """
        Analyze trade-offs using semantic similarity

        Args:
            product: Product data
            preferences: Extracted user preferences
            query_embedding: CLIP embedding of user query

        Returns:
            Trade-off analysis with explainability
        """
        gains = []
        loses = []

        # Generate product embedding
        product_text = self._build_product_text(product)
        product_embedding = self._get_text_embedding(product_text)

        # Budget analysis
        if preferences.get("budget"):
            budget_analysis = self._analyze_budget(product, preferences["budget"])
            gains.extend(budget_analysis["gains"])
            loses.extend(budget_analysis["loses"])

        # Material analysis using semantic similarity
        if preferences.get("material"):
            material_analysis = self._analyze_material(
                product, preferences["material"], query_embedding, product_embedding
            )
            gains.extend(material_analysis["gains"])
            loses.extend(material_analysis["loses"])

        # Style analysis using semantic similarity
        if preferences.get("style"):
            style_analysis = self._analyze_style(
                product, preferences["style"], query_embedding, product_embedding
            )
            gains.extend(style_analysis["gains"])
            loses.extend(style_analysis["loses"])

        # Comfort analysis
        if preferences.get("comfort"):
            comfort_analysis = self._analyze_comfort(
                product, preferences["comfort"], query_embedding, product_embedding
            )
            gains.extend(comfort_analysis["gains"])
            loses.extend(comfort_analysis["loses"])

        # Calculate overall similarity score
        similarity_score = self.extractor._cosine_similarity(query_embedding, product_embedding)

        return {
            "gains": gains,
            "loses": loses,
            "score": len(gains) - len(loses),
            "is_compromise": len(loses) > 0,
            "similarity": float(similarity_score),
            "match_explanation": self._generate_match_explanation(similarity_score)
        }

    def _build_product_text(self, product: dict) -> str:
        """Build rich text description of product for embedding"""
        parts = [
            product.get('name', ''),
            product.get('description', ''),
            ' '.join(product.get('tags', [])),
            ' '.join(product.get('styles', [])),
            ' '.join(product.get('colors', [])),
            f"price {product.get('price', 0)}"
        ]
        return ' '.join(parts)

    def _get_text_embedding(self, text: str) -> np.ndarray:
        """Get CLIP embedding for text"""
        inputs = self.clip_processor(
            text=[text],
            return_tensors="pt",
            padding=True,
            truncation=True
        )
        features = self.clip_model.get_text_features(**inputs)
        return features.detach().numpy()[0]

    def _analyze_budget(self, product: dict, budget: float) -> dict:
        """Analyze budget fit"""
        gains = []
        loses = []

        price = product.get('price', 0)
        if price <= budget:
            savings = budget - price
            if savings > 0:
                gains.append(f"✓ Under budget by ${savings:.0f} (${price:.0f} vs ${budget:.0f})")
            else:
                gains.append(f"✓ Exactly your budget of ${budget:.0f}")
        else:
            overage = price - budget
            loses.append(f"✗ Over budget by ${overage:.0f} (${price:.0f} vs ${budget:.0f})")

        return {"gains": gains, "loses": loses}

    def _analyze_material(
        self,
        product: dict,
        preferred_material: str,
        query_embedding: np.ndarray,
        product_embedding: np.ndarray
    ) -> dict:
        """
        Analyze material fit using semantic similarity

        Compares:
        1. Direct material match
        2. Semantic similarity to preferred material
        3. Alternative materials with explanations
        """
        gains = []
        loses = []

        product_text = self._build_product_text(product).lower()
        preferred_material = preferred_material.lower()

        # Get embedding similarity for preferred material
        material_embedding = self.extractor.attribute_embeddings[preferred_material]
        material_similarity = self.extractor._cosine_similarity(product_embedding, material_embedding)

        # Check for exact or variant match
        if preferred_material in product_text:
            if preferred_material == "leather":
                if "genuine" in product_text or "real" in product_text:
                    gains.append("✓ Genuine leather material (premium quality)")
                else:
                    gains.append("✓ Leather material")
            else:
                gains.append(f"✓ {preferred_material.capitalize()} material")

        # Check for alternatives using similarity
        elif material_similarity > 0.25:
            # Semantically similar but not exact match
            if preferred_material == "leather":
                if "pu" in product_text or "faux" in product_text:
                    loses.append("✗ PU/faux leather (not genuine leather)")
                    gains.append("✓ Leather-like appearance (more affordable)")
                elif "fabric" in product_text or "velvet" in product_text:
                    loses.append(f"✗ Not leather material")
                    # Check which material it is
                    for mat in ["velvet", "fabric", "linen"]:
                        if mat in product_text:
                            gains.append(f"✓ {mat.capitalize()} (softer than leather)")
                            break
                else:
                    loses.append(f"✗ Different material than requested")
            else:
                loses.append(f"✗ Not {preferred_material} material")

        else:
            # Completely different material
            loses.append(f"✗ Not {preferred_material} material")
            # Find what it actually is
            for mat in ["leather", "velvet", "fabric", "wood", "metal"]:
                if mat in product_text:
                    gains.append(f"✓ {mat.capitalize()} material")
                    break

        return {"gains": gains, "loses": loses}

    def _analyze_style(
        self,
        product: dict,
        preferred_style: str,
        query_embedding: np.ndarray,
        product_embedding: np.ndarray
    ) -> dict:
        """Analyze style fit using semantic similarity"""
        gains = []
        loses = []

        product_text = self._build_product_text(product).lower()
        preferred_style = preferred_style.lower()

        # Get style similarity
        style_embedding = self.extractor.attribute_embeddings[preferred_style]
        style_similarity = self.extractor._cosine_similarity(product_embedding, style_embedding)

        # Check for exact match
        if preferred_style in product_text:
            gains.append(f"✓ {preferred_style.capitalize()} style")

        # Check for related styles using similarity
        elif style_similarity > 0.3:
            # Semantically related style
            related_styles = {
                "modern": ["contemporary", "minimalist", "sleek"],
                "traditional": ["classic", "vintage", "antique"],
                "industrial": ["urban", "metal", "raw"]
            }

            if preferred_style in related_styles:
                for related in related_styles[preferred_style]:
                    if related in product_text:
                        gains.append(f"✓ {related.capitalize()} style (similar to {preferred_style})")
                        break

        # Check for opposite style
        opposites = {
            "modern": ["traditional", "vintage"],
            "traditional": ["modern", "minimalist"],
            "industrial": ["traditional"]
        }

        if preferred_style in opposites:
            for opposite in opposites[preferred_style]:
                if opposite in product_text:
                    loses.append(f"✗ {opposite.capitalize()} style (not {preferred_style})")
                    break

        if len(gains) == 0 and len(loses) == 0:
            loses.append(f"✗ Not {preferred_style} style")

        return {"gains": gains, "loses": loses}

    def _analyze_comfort(
        self,
        product: dict,
        preferred_comfort: str,
        query_embedding: np.ndarray,
        product_embedding: np.ndarray
    ) -> dict:
        """Analyze comfort level using semantic similarity"""
        gains = []
        loses = []

        product_text = self._build_product_text(product).lower()

        # Comfort indicators
        comfort_indicators = {
            "high": ["plush", "cushioned", "padded", "soft", "comfy", "cozy"]
        }

        if preferred_comfort == "high":
            if any(indicator in product_text for indicator in comfort_indicators["high"]):
                gains.append("✓ Comfortable cushioning")
            else:
                loses.append("✗ May not be as comfortable as requested")

        return {"gains": gains, "loses": loses}

    def _generate_match_explanation(self, similarity_score: float) -> str:
        """Generate human-readable explanation of similarity score"""
        if similarity_score > 0.8:
            return "Excellent match - highly aligned with your preferences"
        elif similarity_score > 0.6:
            return "Good match - well-aligned with your preferences"
        elif similarity_score > 0.4:
            return "Moderate match - partially aligned with your preferences"
        else:
            return "Loose match - consider the trade-offs carefully"


# Global instances (initialized at startup)
attribute_extractor = None
tradeoff_analyzer = None


def initialize_embedding_system(clip_model, clip_processor):
    """
    Initialize the embedding-based trade-off system

    Call this during FastAPI startup
    """
    global attribute_extractor, tradeoff_analyzer

    attribute_extractor = EmbeddingAttributeExtractor(clip_model, clip_processor)
    tradeoff_analyzer = EmbeddingTradeoffAnalyzer(
        clip_model,
        clip_processor,
        attribute_extractor
    )

    print("✅ Embedding-based trade-off system initialized")

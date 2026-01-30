"""
AI-Powered Product Comparison Engine
Shows side-by-side comparison with visual explanations
"""
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import util

class ProductComparator:
    def __init__(self, clip_model, clip_processor):
        self.clip_model = clip_model
        self.clip_processor = clip_processor
    
    def compare_products(self, product_a: Dict, product_b: Dict) -> Dict[str, Any]:
        """
        Compare two products across multiple dimensions with AI-powered insights
        
        Returns detailed comparison showing:
        - Visual similarity score
        - Price difference with recommendation
        - Feature comparison
        - Style compatibility
        - AI recommendation on which to choose
        """
        
        # 1. Visual Similarity (using CLIP)
        visual_similarity = self._calculate_visual_similarity(product_a, product_b)
        
        # 2. Price Analysis
        price_analysis = self._analyze_price(product_a, product_b)
        
        # 3. Feature Comparison
        feature_comparison = self._compare_features(product_a, product_b)
        
        # 4. Style Analysis
        style_analysis = self._analyze_styles(product_a, product_b)
        
        # 5. AI Recommendation
        ai_recommendation = self._generate_recommendation(
            product_a, product_b, visual_similarity, price_analysis, feature_comparison
        )
        
        return {
            "product_a": {
                "id": product_a.get("id"),
                "name": product_a.get("name"),
                "price": product_a.get("price"),
                "image": product_a.get("image")
            },
            "product_b": {
                "id": product_b.get("id"),
                "name": product_b.get("name"),
                "price": product_b.get("price"),
                "image": product_b.get("image")
            },
            "visual_similarity": {
                "score": round(visual_similarity, 3),
                "explanation": self._explain_visual_similarity(visual_similarity),
                "verdict": "Nearly identical" if visual_similarity > 0.9 else 
                          "Very similar" if visual_similarity > 0.8 else
                          "Somewhat similar" if visual_similarity > 0.6 else
                          "Quite different"
            },
            "price_analysis": price_analysis,
            "feature_comparison": feature_comparison,
            "style_analysis": style_analysis,
            "ai_recommendation": ai_recommendation,
            "comparison_score": self._calculate_overall_score(product_a, product_b, visual_similarity)
        }
    
    def _calculate_visual_similarity(self, product_a: Dict, product_b: Dict) -> float:
        """Calculate visual similarity using CLIP embeddings"""
        # For demo: use product names as proxy (in production, use actual image embeddings)
        name_a = product_a.get("name", "")
        name_b = product_b.get("name", "")
        
        # Generate text embeddings
        inputs_a = self.clip_processor(text=[name_a], return_tensors="pt", padding=True)
        inputs_b = self.clip_processor(text=[name_b], return_tensors="pt", padding=True)
        
        features_a = self.clip_model.get_text_features(**inputs_a)
        features_b = self.clip_model.get_text_features(**inputs_b)
        
        # Calculate cosine similarity
        similarity = util.cos_sim(features_a, features_b)[0][0].item()
        return similarity
    
    def _analyze_price(self, product_a: Dict, product_b: Dict) -> Dict:
        """Analyze price difference and value proposition"""
        price_a = product_a.get("price", 0)
        price_b = product_b.get("price", 0)
        diff = price_b - price_a
        percent_diff = (diff / price_a * 100) if price_a > 0 else 0
        
        if abs(diff) < 10:
            verdict = "Similar pricing"
        elif diff > 0:
            verdict = f"${abs(diff)} more expensive ({abs(percent_diff):.1f}% premium)"
        else:
            verdict = f"${abs(diff)} cheaper ({abs(percent_diff):.1f}% savings)"
        
        return {
            "product_a_price": price_a,
            "product_b_price": price_b,
            "difference": diff,
            "percent_difference": round(percent_diff, 1),
            "verdict": verdict,
            "better_value": "product_a" if price_a < price_b else "product_b" if price_b < price_a else "equal"
        }
    
    def _compare_features(self, product_a: Dict, product_b: Dict) -> Dict:
        """Compare product features"""
        features_a = set(product_a.get("features", []))
        features_b = set(product_b.get("features", []))
        
        common = features_a & features_b
        unique_a = features_a - features_b
        unique_b = features_b - features_a
        
        return {
            "common_features": list(common),
            "unique_to_a": list(unique_a),
            "unique_to_b": list(unique_b),
            "feature_overlap": len(common) / max(len(features_a), len(features_b), 1)
        }
    
    def _analyze_styles(self, product_a: Dict, product_b: Dict) -> Dict:
        """Analyze style compatibility"""
        styles_a = set(s.lower() for s in product_a.get("styles", []))
        styles_b = set(s.lower() for s in product_b.get("styles", []))
        
        common_styles = styles_a & styles_b
        
        if len(common_styles) >= 2:
            compatibility = "Highly compatible styles"
        elif len(common_styles) == 1:
            compatibility = "Somewhat compatible styles"
        else:
            compatibility = "Different style aesthetics"
        
        return {
            "product_a_styles": list(styles_a),
            "product_b_styles": list(styles_b),
            "common_styles": list(common_styles),
            "compatibility": compatibility
        }
    
    def _generate_recommendation(self, product_a, product_b, visual_sim, price_analysis, feature_comp):
        """Generate AI recommendation on which product to choose"""
        
        # Score each product
        score_a = 0
        score_b = 0
        reasons_a = []
        reasons_b = []
        
        # Price factor
        if price_analysis["better_value"] == "product_a":
            score_a += 10
            reasons_a.append(f"Better value (${price_analysis['difference']} cheaper)")
        elif price_analysis["better_value"] == "product_b":
            score_b += 10
            reasons_b.append(f"Better value (${abs(price_analysis['difference'])} cheaper)")
        
        # Features factor
        if len(feature_comp["unique_to_a"]) > len(feature_comp["unique_to_b"]):
            score_a += 5
            reasons_a.append(f"More features (+{len(feature_comp['unique_to_a'])})")
        elif len(feature_comp["unique_to_b"]) > len(feature_comp["unique_to_a"]):
            score_b += 5
            reasons_b.append(f"More features (+{len(feature_comp['unique_to_b'])})")
        
        # Determine winner
        if score_a > score_b:
            winner = "product_a"
            confidence = min(90, 60 + (score_a - score_b) * 5)
            recommendation = f"Product A is the better choice"
        elif score_b > score_a:
            winner = "product_b"
            confidence = min(90, 60 + (score_b - score_a) * 5)
            recommendation = f"Product B is the better choice"
        else:
            winner = "tie"
            confidence = 50
            recommendation = "Both products are equally good - choose based on personal preference"
        
        return {
            "winner": winner,
            "confidence": confidence,
            "recommendation": recommendation,
            "reasons_for_a": reasons_a if reasons_a else ["Solid choice"],
            "reasons_for_b": reasons_b if reasons_b else ["Solid choice"],
            "visual_similarity_note": "Products are visually similar" if visual_sim > 0.7 else "Products have different aesthetics"
        }
    
    def _explain_visual_similarity(self, score: float) -> str:
        """Generate human-readable explanation of visual similarity"""
        if score > 0.9:
            return "These products look almost identical - likely same style/design family"
        elif score > 0.8:
            return "Very similar visual appearance - you'd get nearly the same look"
        elif score > 0.6:
            return "Moderately similar - same category but noticeable differences"
        else:
            return "Quite different visually - distinct designs"
    
    def _calculate_overall_score(self, product_a, product_b, visual_sim) -> float:
        """Overall comparison score (0-100)"""
        # Higher score = more similar products
        price_a = product_a.get("price", 0)
        price_b = product_b.get("price", 0)
        price_similarity = 1 - min(abs(price_a - price_b) / max(price_a, price_b, 1), 1)
        
        overall = (visual_sim * 0.6 + price_similarity * 0.4) * 100
        return round(overall, 1)

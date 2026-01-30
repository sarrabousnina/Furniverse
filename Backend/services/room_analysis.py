import sys
import os
from pathlib import Path
import numpy as np
from PIL import Image
import io
import base64
from collections import Counter
from typing import Dict, List, Optional, Tuple

# Add Pipeline to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Pipeline'))

from cv.detector import FurnitureDetector
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import qdrant_config

class RoomAnalyzer:
    def __init__(self, clip_model, clip_processor, qdrant_client):
        self.detector = FurnitureDetector()
        self.clip_model = clip_model
        self.clip_processor = clip_processor
        self.qdrant_client = qdrant_client
        
        # Essential furniture for each room type (rule-based system)
        self.room_essentials = {
            "living_room": {
                "required": ["sofa", "coffee table"],
                "recommended": ["side table", "lamp", "tv stand", "bookshelf", "rug"],
                "categories": ["sofas", "tables", "chairs", "lamps", "storage"]
            },
            "bedroom": {
                "required": ["bed", "nightstand"],
                "recommended": ["dresser", "chair", "lamp", "mirror", "wardrobe"],
                "categories": ["beds", "tables", "chairs", "lamps", "storage"]
            },
            "office": {
                "required": ["desk", "office chair"],
                "recommended": ["bookshelf", "lamp", "storage", "side table"],
                "categories": ["tables", "chairs", "lamps", "storage"]
            },
            "dining_room": {
                "required": ["dining table", "dining chair"],
                "recommended": ["buffet", "lamp", "bar cart", "mirror"],
                "categories": ["tables", "chairs", "storage", "lamps"]
            },
            "kitchen": {
                "required": ["dining table", "chair"],
                "recommended": ["bar stool", "cart", "storage"],
                "categories": ["tables", "chairs", "storage"]
            },
            "bathroom": {
                "required": ["storage"],
                "recommended": ["mirror", "stool", "cabinet"],
                "categories": ["storage", "chairs"]
            }
        }
        
        # Style-furniture compatibility matrix
        self.style_furniture_mapping = {
            "modern": {"sofa": "sectional", "chair": "accent chair", "table": "glass table"},
            "scandinavian": {"sofa": "loveseat", "chair": "wooden chair", "table": "wooden table"},
            "industrial": {"sofa": "leather sofa", "chair": "metal chair", "table": "metal table"},
            "minimalist": {"sofa": "simple sofa", "chair": "clean-lined chair", "table": "simple table"}
        }
    
    def determine_room_type(self, detected_furniture: List[Dict], user_room_type: Optional[str] = None) -> str:
        """Determine room type using rule-based system if not provided by user"""
        if user_room_type:
            return user_room_type.lower().replace(' ', '_')
        
        # Count furniture types
        furniture_counts = Counter([item['class'].lower() for item in detected_furniture])
        
        # Rule-based room type detection
        if 'bed' in furniture_counts:
            return 'bedroom'
        elif 'sofa' in furniture_counts or 'couch' in furniture_counts:
            return 'living_room'
        elif 'desk' in furniture_counts and 'chair' in furniture_counts:
            return 'office'
        elif 'dining table' in furniture_counts or any('dining' in f for f in furniture_counts):
            return 'dining_room'
        elif furniture_counts.get('chair', 0) >= 2 and 'table' in furniture_counts:
            return 'dining_room'
        else:
            return 'living_room'  # Default fallback
    
    def identify_missing_furniture(self, detected_furniture: List[Dict], room_type: str) -> Dict:
        """Identify missing essential and recommended furniture for the room type"""
        if room_type not in self.room_essentials:
            return {"missing_required": [], "missing_recommended": []}
        
        detected_types = {item['class'].lower() for item in detected_furniture}
        room_config = self.room_essentials[room_type]
        
        # Find missing required furniture
        missing_required = [
            item for item in room_config["required"] 
            if not any(req.lower() in det for det in detected_types for req in [item])
        ]
        
        # Find missing recommended furniture
        missing_recommended = [
            item for item in room_config["recommended"] 
            if not any(rec.lower() in det for det in detected_types for rec in [item])
        ]
        
        return {
            "missing_required": missing_required,
            "missing_recommended": missing_recommended[:3],  # Limit to top 3 recommendations
            "room_essentials": room_config
        }
    
    def get_style_based_recommendations(self, missing_items: List[str], room_style: str, 
                                      budget_min: Optional[int] = None, budget_max: Optional[int] = None) -> List[Dict]:
        """Get product recommendations for missing furniture based on style and budget"""
        recommendations = []
        
        for item in missing_items:
            try:
                # Create search query based on style and item
                search_query = f"{room_style.lower()} {item}"
                
                # Get CLIP embedding for search query
                inputs = self.clip_processor(text=[search_query], return_tensors="pt", padding=True, truncation=True)
                text_features = self.clip_model.get_text_features(**inputs)
                query_embedding = text_features.detach().numpy()[0].tolist()
                
                # Determine category filter based on item type
                category_filter = self._get_category_for_item(item)
                
                # Build search filters
                filters_list = []
                if category_filter:
                    filters_list.append(FieldCondition(key="category", match=MatchValue(value=category_filter)))
                
                # Add price filter if budget provided
                if budget_min is not None and budget_max is not None and budget_min > 0 and budget_max > 0:
                    filters_list.append(FieldCondition(key="price", range={"gte": float(budget_min), "lte": float(budget_max)}))
                
                search_filter = Filter(must=filters_list) if filters_list else None
                
                # Search for similar products
                results = self.qdrant_client.search(
                    collection_name=qdrant_config.COLLECTION_PRODUCTS,
                    query_vector=("text_clip", query_embedding),
                    query_filter=search_filter,
                    limit=5,  # Get more products per item
                    with_payload=True,
                    score_threshold=0.25
                )
                
                # Format recommendations
                item_recommendations = []
                for result in results:
                    payload = result.payload
                    item_recommendations.append({
                        "product_id": str(payload.get('product_id', result.id)),
                        "name": payload.get('name', ''),
                        "category": payload.get('category', ''),
                        "price": float(payload.get('price', 0)),
                        "image": payload.get('image', ''),
                        "similarity_score": float(result.score),
                        "styles": payload.get('styles', []),
                        "description": payload.get('description', ''),
                        "colors": payload.get('colors', []),
                        "rating": payload.get('rating', 0),
                        "reviewCount": payload.get('reviewCount', 0)
                    })
                
                if item_recommendations:
                    recommendations.append({
                        "category": item,
                        "furniture_type": item,
                        "products": item_recommendations,
                        "similarity_score": item_recommendations[0]['similarity_score'] if item_recommendations else 0
                    })
                    
            except Exception as e:
                print(f"Error getting recommendations for {item}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        return recommendations
    
    def _get_category_for_item(self, item: str) -> Optional[str]:
        """Map furniture item to product category"""
        category_mapping = {
            "sofa": "sofas", "couch": "sofas", "sectional": "sofas", "loveseat": "sofas",
            "chair": "chairs", "armchair": "chairs", "accent chair": "chairs", "office chair": "chairs",
            "table": "tables", "coffee table": "tables", "dining table": "tables", "desk": "tables", "side table": "tables",
            "bed": "beds", "nightstand": "tables", "dresser": "storage", "bookshelf": "storage",
            "lamp": "lamps", "floor lamp": "lamps", "table lamp": "lamps",
            "storage": "storage", "cabinet": "storage", "wardrobe": "storage"
        }
        
        item_lower = item.lower()
        for key, category in category_mapping.items():
            if key in item_lower:
                return category
        
        return None
    
    def analyze_room_with_suggestions(self, image_data: str, room_type: Optional[str] = None, 
                                    budget_min: Optional[int] = None, budget_max: Optional[int] = None,
                                    existing_furniture: Optional[str] = None) -> Dict:
        """Complete room analysis with missing furniture suggestions"""
        # Convert base64 to PIL Image
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_array = np.array(image)
        
        # Detect furniture
        detections = self.detector.detect(image_array, conf=0.5)
        
        # Basic analysis for empty rooms
        if not detections:
            determined_room_type = room_type.lower().replace(' ', '_') if room_type else 'living_room'
            missing_analysis = self.identify_missing_furniture([], determined_room_type)
            
            # Get recommendations for all essential items
            all_missing = missing_analysis["missing_required"] + missing_analysis["missing_recommended"]
            recommendations = self.get_style_based_recommendations(
                all_missing[:5], "modern", budget_min, budget_max  # Default to modern style
            )
            
            return {
                "detected_furniture": [],
                "room_style": "Unknown",
                "style_confidence": 0.0,
                "room_type": determined_room_type,
                "missing_furniture": missing_analysis,
                "recommendations": recommendations,
                "analysis_summary": f"No furniture detected. Here are essential items for your {determined_room_type.replace('_', ' ')}."
            }
        
        # Crop detected objects and analyze style using CLIP
        style_scores = []
        detected_furniture = []
        
        # Define style prompts for CLIP classification
        style_prompts = [
            "modern minimalist furniture",
            "scandinavian furniture with natural wood",
            "industrial furniture with metal and leather",
            "traditional classic furniture",
            "contemporary furniture",
            "rustic farmhouse furniture",
            "mid-century modern furniture",
            "bohemian eclectic furniture"
        ]
        
        # Get embeddings for style prompts once
        style_inputs = self.clip_processor(text=style_prompts, return_tensors="pt", padding=True, truncation=True)
        style_text_features = self.clip_model.get_text_features(**style_inputs)
        style_embeddings = style_text_features.detach().numpy()
        
        for detection in detections:
            x1, y1, x2, y2 = [int(coord) for coord in detection['box']]
            cropped = image.crop((x1, y1, x2, y2))
            
            # Get CLIP embedding for cropped furniture
            inputs = self.clip_processor(images=cropped, return_tensors="pt", padding=True)
            image_features = self.clip_model.get_image_features(**inputs)
            crop_embedding = image_features.detach().numpy()[0]
            
            # Calculate cosine similarity with each style
            from numpy.linalg import norm
            item_style_scores = {}
            for i, style_prompt in enumerate(style_prompts):
                style_name = style_prompt.split()[0]  # Extract style name
                similarity = np.dot(crop_embedding, style_embeddings[i]) / (norm(crop_embedding) * norm(style_embeddings[i]))
                item_style_scores[style_name] = float(similarity)
            
            style_scores.append(item_style_scores)
            
            # Find most similar product in database for category matching
            try:
                crop_embedding_list = crop_embedding.tolist()
                results = self.qdrant_client.search(
                    collection_name=qdrant_config.COLLECTION_PRODUCTS,
                    query_vector=("image_clip", crop_embedding_list),
                    limit=1,
                    with_payload=True
                )
                
                if results:
                    best_match = results[0]
                    detected_furniture.append({
                        "class": detection['class'],
                        "confidence": detection['confidence'],
                        "matched_product": best_match.payload.get('name', ''),
                        "similarity": best_match.score,
                        "matched_category": best_match.payload.get('category', ''),
                        "detected_style_scores": item_style_scores
                    })
                else:
                    detected_furniture.append({
                        "class": detection['class'],
                        "confidence": detection['confidence'],
                        "detected_style_scores": item_style_scores
                    })
            except Exception as e:
                print(f"Error matching furniture: {e}")
                detected_furniture.append({
                    "class": detection['class'],
                    "confidence": detection['confidence'],
                    "detected_style_scores": item_style_scores
                })
        
        # Determine room type and style
        determined_room_type = self.determine_room_type(detected_furniture, room_type)
        
        # Aggregate style scores across all detected furniture
        if style_scores:
            aggregated_scores = {}
            for item_scores in style_scores:
                for style, score in item_scores.items():
                    aggregated_scores[style] = aggregated_scores.get(style, 0) + score
            
            # Find dominant style
            dominant_style = max(aggregated_scores.items(), key=lambda x: x[1])[0]
            total_score = sum(aggregated_scores.values())
            style_confidence = aggregated_scores[dominant_style] / total_score if total_score > 0 else 0.0
            dominant_style = dominant_style.capitalize()
        else:
            dominant_style = "Modern"  # Default fallback
            style_confidence = 0.0
        
        # Identify missing furniture
        missing_analysis = self.identify_missing_furniture(detected_furniture, determined_room_type)
        
        # Get recommendations for missing items
        all_missing = missing_analysis["missing_required"] + missing_analysis["missing_recommended"]
        recommendations = self.get_style_based_recommendations(
            all_missing, dominant_style, budget_min, budget_max
        )
        
        # Generate analysis summary
        summary_parts = []
        if missing_analysis["missing_required"]:
            summary_parts.append(f"Essential items missing: {', '.join(missing_analysis['missing_required'])}")
        if missing_analysis["missing_recommended"]:
            summary_parts.append(f"Recommended additions: {', '.join(missing_analysis['missing_recommended'][:3])}")
        if not summary_parts:
            summary_parts.append("Your room looks well-furnished! Here are some style-matched additions you might consider.")
        
        return {
            "detected_furniture": detected_furniture,
            "room_style": dominant_style,
            "style_confidence": round(style_confidence, 2),
            "room_type": determined_room_type,
            "missing_furniture": missing_analysis,
            "recommendations": recommendations,
            "analysis_summary": " ".join(summary_parts)
        }
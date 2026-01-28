"""
User Activity Tracking and Product → User Recommendations
Stores user interactions in Qdrant and enables finding users interested in specific products
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

# Add Pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'Pipeline'))

from embeddings.engine import EmbeddingEngine
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, VectorParams, Distance
import qdrant_config


# Local cache for recent activity (still use this for quick access)
user_activities_cache = defaultdict(list)


class UserEvent:
    """User interaction event"""

    def __init__(self, user_id: str, event_type: str, product_id: str,
                 product_name: str, category: str, price: float,
                 search_query: Optional[str] = None):
        self.user_id = user_id
        self.event_type = event_type  # 'view', 'click', 'search'
        self.product_id = product_id
        self.product_name = product_name
        self.category = category
        self.price = price
        self.search_query = search_query
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'event_type': self.event_type,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'category': self.category,
            'price': self.price,
            'search_query': self.search_query,
            'timestamp': self.timestamp
        }


class UserActivityTracker:
    """Track user interactions and store user preference embeddings in Qdrant"""

    def __init__(self):
        self.qdrant_client = QdrantClient(
            url=qdrant_config.QDRANT_URL,
            api_key=qdrant_config.QDRANT_API_KEY
        )
        self.embedding_engine = EmbeddingEngine(
            qdrant_url=qdrant_config.QDRANT_URL,
            qdrant_api_key=qdrant_config.QDRANT_API_KEY
        )

        # Create users collection if it doesn't exist
        self._create_users_collection()

    def _create_users_collection(self):
        """Create the users collection in Qdrant for Product → User recommendations"""
        try:
            self.qdrant_client.get_collection('users')
            print("[OK] Users collection already exists")
        except:
            # Create collection with named vectors
            self.qdrant_client.create_collection(
                collection_name='users',
                vectors_config={
                    'preference': VectorParams(size=512, distance=Distance.COSINE),
                    'graph_neighborhood': VectorParams(size=256, distance=Distance.COSINE)
                }
            )
            print("[OK] Created users collection in Qdrant")

    def _get_user_point_id(self, user_id: str) -> int:
        """Convert string user_id to integer point ID for Qdrant"""
        return hash(user_id) % (2**31)

    def track_event(self, event: UserEvent):
        """
        Store a user interaction event in Qdrant
        Updates user preference embedding with each new event
        """
        # Cache locally for quick access
        user_activities_cache[event.user_id].append(event.to_dict())

        # Update user embedding in Qdrant
        self._update_user_embedding_in_qdrant(event.user_id)

    def _update_user_embedding_in_qdrant(self, user_id: str):
        """
        Compute and store user preference embedding in Qdrant
        Combines recent product views, clicks, and search queries
        """
        events = user_activities_cache.get(user_id, [])

        if not events:
            return

        # Build user profile text from recent events (last 50)
        profile_texts = []
        for event in events[-50:]:
            if event['event_type'] == 'search' and event.get('search_query'):
                profile_texts.append(event['search_query'])
            elif event['event_type'] in ['view', 'click']:
                profile_texts.append(f"{event.get('product_name', '')} {event.get('category', '')}")

        if not profile_texts:
            return

        # Combine all profile text
        combined_profile = " ".join(profile_texts)

        # Generate embedding using CLIP (same as product embeddings)
        try:
            # Use CLIP text encoder
            text_features = self.embedding_engine.clip.encode_text(combined_profile)
            user_embedding = text_features[0]

            # Prepare payload with user activity summary
            recent_events = events[-100:]  # Last 100 events
            payload = {
                'user_id': user_id,
                'total_events': len(events),
                'last_updated': datetime.now().isoformat(),
                'recent_activity': recent_events,
                # Extract categories for filtering
                'categories': list(set([e.get('category', '') for e in events if e.get('category')]))
            }

            # Upsert to Qdrant (create or update user point)
            point_id = self._get_user_point_id(user_id)

            self.qdrant_client.upsert(
                collection_name='users',
                points=[PointStruct(
                    id=point_id,
                    vector={
                        'preference': user_embedding.tolist()
                    },
                    payload=payload
                )]
            )

        except Exception as e:
            print(f"Failed to update user embedding in Qdrant: {e}")

    def find_interested_users(self, product_id: str, product_name: str,
                              category: str, limit: int = 10) -> List[Dict]:
        """
        Product → User Recommendation: Find users interested in a product using Qdrant

        Uses semantic similarity between product and user preference embeddings in Qdrant
        """
        try:
            # Generate product embedding using CLIP
            product_text = f"{product_name} {category}"
            product_embedding = self.embedding_engine.clip.encode_text(product_text)[0]

            # Search in Qdrant for similar users
            results = self.qdrant_client.search(
                collection_name='users',
                query_vector=('preference', product_embedding.tolist()),
                limit=limit,
                with_payload=True,
                score_threshold=0.1  # Only return reasonably similar users
            )

            # Format results
            interested_users = []
            for result in results:
                payload = result.payload
                recent_activity = payload.get('recent_activity', [])

                # Count activity in last 30 days
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_count = sum(
                    1 for e in recent_activity
                    if datetime.fromisoformat(e['timestamp']) > thirty_days_ago
                )

                interested_users.append({
                    'user_id': payload.get('user_id'),
                    'similarity_score': float(result.score),
                    'activity_count': recent_count,
                    'last_active': max([e['timestamp'] for e in recent_activity]) if recent_activity else None
                })

            return interested_users

        except Exception as e:
            print(f"Failed to find interested users: {e}")
            return []

    def get_user_activity_summary(self, user_id: str) -> Dict:
        """Get summary of user activity from Qdrant"""
        try:
            point_id = self._get_user_point_id(user_id)

            # Retrieve user point from Qdrant
            points = self.qdrant_client.retrieve(
                collection_name='users',
                ids=[point_id],
                with_payload=True
            )

            if not points or len(points) == 0:
                return {
                    'user_id': user_id,
                    'total_events': 0,
                    'product_views': 0,
                    'product_clicks': 0,
                    'searches': 0,
                    'top_categories': {},
                    'last_active': None,
                    'found': False
                }

            payload = points[0].payload
            recent_activity = payload.get('recent_activity', [])

            # Count events
            views = [e for e in recent_activity if e['event_type'] == 'view']
            clicks = [e for e in recent_activity if e['event_type'] == 'click']
            searches = [e for e in recent_activity if e['event_type'] == 'search']

            # Top categories
            category_counts = defaultdict(int)
            for event in recent_activity:
                if event.get('category'):
                    category_counts[event['category']] += 1

            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                'user_id': user_id,
                'total_events': payload.get('total_events', len(recent_activity)),
                'product_views': len(views),
                'product_clicks': len(clicks),
                'searches': len(searches),
                'top_categories': dict(top_categories),
                'last_active': payload.get('last_updated'),
                'found': True
            }

        except Exception as e:
            print(f"Failed to get user activity: {e}")
            return {
                'user_id': user_id,
                'error': str(e)
            }


# Global tracker instance
tracker = UserActivityTracker()

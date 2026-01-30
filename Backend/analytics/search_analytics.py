"""
Real-time Search Analytics Dashboard
Perfect for hackathon demo - shows AI working in real-time!
"""
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List
import threading

class SearchAnalytics:
    def __init__(self, max_history=100):
        self.searches = deque(maxlen=max_history)  # Recent searches
        self.category_counts = defaultdict(int)
        self.price_ranges = defaultdict(int)
        self.popular_keywords = defaultdict(int)
        self.lock = threading.Lock()
        
    def track_search(self, query: str, category: str = None, results_count: int = 0):
        """Track a search query"""
        with self.lock:
            search_data = {
                "query": query,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "results_count": results_count
            }
            self.searches.append(search_data)
            
            # Update category stats
            if category and category != 'all':
                self.category_counts[category] += 1
            
            # Extract keywords (simple version)
            keywords = query.lower().split()
            for keyword in keywords:
                if len(keyword) > 3:  # Ignore short words
                    self.popular_keywords[keyword] += 1
    
    def get_live_stats(self) -> Dict:
        """Get real-time search statistics"""
        with self.lock:
            # Recent searches (last 20)
            recent = list(self.searches)[-20:]
            
            # Top categories
            top_categories = sorted(
                self.category_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Top keywords
            top_keywords = sorted(
                self.popular_keywords.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Calculate search trends (last hour)
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            recent_searches_count = sum(
                1 for s in self.searches
                if datetime.fromisoformat(s["timestamp"]) > hour_ago
            )
            
            return {
                "total_searches": len(self.searches),
                "searches_last_hour": recent_searches_count,
                "recent_searches": recent,
                "top_categories": [
                    {"category": cat, "count": count}
                    for cat, count in top_categories
                ],
                "trending_keywords": [
                    {"keyword": kw, "count": count}
                    for kw, count in top_keywords
                ],
                "average_results": sum(s.get("results_count", 0) for s in self.searches) / max(len(self.searches), 1),
                "timestamp": now.isoformat()
            }
    
    def get_search_heatmap(self) -> Dict:
        """Generate search pattern heatmap data"""
        with self.lock:
            # Group searches by hour
            hourly_data = defaultdict(int)
            
            for search in self.searches:
                timestamp = datetime.fromisoformat(search["timestamp"])
                hour = timestamp.hour
                hourly_data[hour] += 1
            
            return {
                "hourly_distribution": [
                    {"hour": h, "searches": hourly_data.get(h, 0)}
                    for h in range(24)
                ]
            }

# Global analytics instance
analytics = SearchAnalytics()

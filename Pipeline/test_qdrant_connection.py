"""
Test Qdrant Cloud Connection

Quick script to verify your Qdrant Cloud credentials are working.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

import qdrant_config
from qdrant_client import QdrantClient


def test_connection():
    """Test connection to Qdrant Cloud"""
    
    print("="*80)
    print("QDRANT CLOUD CONNECTION TEST")
    print("="*80)
    
    print(f"\nConnecting to: {qdrant_config.QDRANT_URL}")
    print("API Key: ***" + qdrant_config.QDRANT_API_KEY[-10:])
    
    try:
        # Connect to Qdrant Cloud
        client = QdrantClient(
            url=qdrant_config.QDRANT_URL,
            api_key=qdrant_config.QDRANT_API_KEY
        )
        
        # Get collections
        collections = client.get_collections()
        
        print("\n✓ Connection successful!")
        print(f"\nExisting collections: {len(collections.collections)}")
        
        for collection in collections.collections:
            print(f"  - {collection.name}")
        
        if not collections.collections:
            print("  (No collections yet - will be created during indexing)")
        
        print("\n" + "="*80)
        print("✓ QDRANT CLOUD IS READY!")
        print("="*80)
        print("\nYou can now run:")
        print("  cd Pipeline/indexing")
        print("  python index_qdrant.py")
        
        return True
        
    except Exception as e:
        print("\n✗ Connection failed!")
        print(f"\nError: {e}")
        print("\nPlease check:")
        print("  1. Your Qdrant Cloud URL is correct")
        print("  2. Your API key is valid")
        print("  3. You have internet connection")
        
        return False


if __name__ == '__main__':
    test_connection()

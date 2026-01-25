"""
Quick Setup and Indexing Script for Furniverse

This script automates the complete indexing pipeline:
1. Checks Qdrant connection
2. Installs dependencies
3. Runs product indexing
4. Verifies the results

Run with: python run_indexing.py
"""

import subprocess
import sys
import time
from pathlib import Path


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def check_qdrant_connection() -> bool:
    """Check if Qdrant Cloud is accessible"""
    try:
        import qdrant_config
        from qdrant_client import QdrantClient
        
        client = QdrantClient(url=qdrant_config.QDRANT_URL, api_key=qdrant_config.QDRANT_API_KEY)
        client.get_collections()
        print(f"✓ Qdrant Cloud is accessible")
        return True
    except Exception as e:
        print(f"✗ Cannot connect to Qdrant Cloud")
        print(f"  Error: {e}")
        return False


def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    if not requirements_file.exists():
        print("⚠ requirements.txt not found")
        return False
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            check=True
        )
        print("✓ All dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def run_product_indexing():
    """Run the main product indexing script"""
    print_header("Indexing Products")
    
    indexing_script = Path(__file__).parent / 'indexing' / 'index_qdrant.py'
    
    if not indexing_script.exists():
        print(f"✗ Indexing script not found: {indexing_script}")
        return False
    
    try:
        subprocess.run(
            [sys.executable, str(indexing_script)],
            check=True,
            cwd=indexing_script.parent
        )
        print("\n✓ Product indexing completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Indexing failed: {e}")
        return False


def run_profile_indexing():
    """Run user and room profile indexing"""
    print_header("Indexing User & Room Profiles")
    
    profile_script = Path(__file__).parent / 'indexing' / 'index_profiles.py'
    
    if not profile_script.exists():
        print(f"⚠ Profile indexing script not found: {profile_script}")
        return False
    
    try:
        subprocess.run(
            [sys.executable, str(profile_script)],
            check=True,
            cwd=profile_script.parent
        )
        print("\n✓ Profile indexing completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Profile indexing failed: {e}")
        return False


def verify_collections():
    """Verify that collections were created successfully"""
    print_header("Verifying Collections")
    
    try:
        import qdrant_config
        from qdrant_client import QdrantClient
        
        client = QdrantClient(url=qdrant_config.QDRANT_URL, api_key=qdrant_config.QDRANT_API_KEY)
        collections = client.get_collections().collections
        
        expected = ['products_multimodal', 'users', 'rooms']
        found = [c.name for c in collections]
        
        print("Collections in Qdrant Cloud:")
        for name in expected:
            if name in found:
                info = client.get_collection(name)
                print(f"  ✓ {name}: {info.points_count} points")
            else:
                print(f"  - {name}: Not found (may not have been indexed yet)")
        
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


def main():
    """Main execution flow"""
    
    print_header("FURNIVERSE INDEXING PIPELINE")
    
    print("This script will:")
    print("  1. Check Qdrant connection")
    print("  2. Install dependencies (if needed)")
    print("  3. Index products with multimodal features")
    print("  4. Index user and room profiles")
    print("  5. Verify the results")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Check Qdrant
    print_header("Step 1: Checking Qdrant Cloud Connection")
    
    if not check_qdrant_connection():
        print("\n⚠ Qdrant Cloud connection failed!")
        print("\nPlease check:")
        print("  1. Your internet connection")
        print("  2. Qdrant Cloud URL in Pipeline/qdrant_config.py")
        print("  3. Qdrant Cloud API key in Pipeline/qdrant_config.py")
        
        response = input("\nDo you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("\nExiting. Please check your Qdrant Cloud settings.")
            return
    
    # Step 2: Install dependencies
    print_header("Step 2: Installing Dependencies")
    
    response = input("Install/update dependencies? (y/n): ")
    if response.lower() == 'y':
        if not install_dependencies():
            print("\n⚠ Dependency installation had issues, but continuing...")
    
    # Step 3: Index products
    print_header("Step 3: Indexing Products")
    
    response = input("Start product indexing? This may take 10-30 minutes. (y/n): ")
    if response.lower() == 'y':
        if not run_product_indexing():
            print("\n✗ Product indexing failed!")
            return
    else:
        print("⚠ Skipping product indexing")
    
    # Step 4: Index profiles
    print_header("Step 4: Indexing Profiles")
    
    response = input("Index user and room profiles? (y/n): ")
    if response.lower() == 'y':
        run_profile_indexing()
    else:
        print("⚠ Skipping profile indexing")
    
    # Step 5: Verify
    print_header("Step 5: Verification")
    verify_collections()
    
    # Done!
    print_header("✓ SETUP COMPLETE!")
    
    print("Your Furniverse vector database is ready in Qdrant Cloud!")
    print("\nNext steps:")
    print("  1. Visit your Qdrant Cloud dashboard to explore collections")
    print("  2. Update Backend API to use Qdrant for recommendations")
    print("  3. Test multimodal search queries")
    print("\nSee INDEXING_GUIDE.md for detailed usage instructions.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

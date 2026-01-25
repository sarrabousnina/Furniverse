"""
Image Downloader for Furniverse Product Catalog
Downloads product images from IKEA URLs and organizes them locally.
Generates updated products.json with local image paths in Data/processed/
"""

import csv
import json
import os
import time
from pathlib import Path
from urllib.request import urlretrieve, Request, urlopen
from urllib.error import URLError, HTTPError
from PIL import Image
import io


# Paths
PROCESSED_DIR = Path("../../Data/processed")
IMAGES_DIR = Path("../../Data/raw/images")
INPUT_CSV = PROCESSED_DIR / "products.csv"
OUTPUT_JSON = PROCESSED_DIR / "products.json"

# Configuration
MAX_IMAGES_PER_PRODUCT = 3  # Download first 3 images per product
TARGET_SIZE = (512, 512)    # Resize for CLIP embeddings
QUALITY = 85                # JPEG quality
DELAY_BETWEEN_DOWNLOADS = 0.5  # Seconds (be nice to IKEA servers)


def download_image(url, save_path, max_retries=3):
    """Download image from URL with retry logic and error handling."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=10) as response:
                img_data = response.read()
            
            # Open and resize image
            img = Image.open(io.BytesIO(img_data))
            img = img.convert('RGB')  # Ensure RGB format
            img.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(save_path, 'JPEG', quality=QUALITY, optimize=True)
            return True
            
        except (URLError, HTTPError, OSError) as e:
            print(f"    ⚠ Attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return False


def load_products_from_csv():
    """Load product data from processed CSV."""
    products = []
    
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse pipe-separated image URLs
            image_urls = row['images'].split('|') if row['images'] else []
            
            product = {
                'id': int(row['id']),
                'name': row['name'],
                'category': row['category'],
                'price': int(row['price']) if row['price'] else 0,
                'rating': float(row['rating']) if row['rating'] else 0.0,
                'reviewCount': int(row['reviewCount']) if row['reviewCount'] else 0,
                'image': row['image'],  # Primary image URL
                'images': image_urls,  # All image URLs
                'description': row['description'],
                'trending': row['trending'].lower() == 'true',
                'dimensions': {
                    'width': int(row['width']) if row['width'] else None,
                    'height': int(row['height']) if row['height'] else None,
                    'depth': int(row['depth']) if row['depth'] else None,
                },
                'features': row['features'].split('|') if row['features'] else [],
                'styles': row['styles'].split(',') if row['styles'] else [],
                'tags': row['tags'].split(',') if row['tags'] else [],
                'colors': row['colors'].split(',') if row['colors'] else [],
            }
            products.append(product)
    
    return products


def download_product_images(products):
    """Download images for all products and update with local paths."""
    # Create images directory
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"DOWNLOADING PRODUCT IMAGES")
    print(f"{'='*60}\n")
    print(f"Total products: {len(products)}")
    print(f"Max images per product: {MAX_IMAGES_PER_PRODUCT}")
    print(f"Target size: {TARGET_SIZE}")
    print(f"Saving to: {IMAGES_DIR.absolute()}\n")
    
    stats = {
        'total_products': len(products),
        'products_with_images': 0,
        'total_images_downloaded': 0,
        'total_images_failed': 0,
    }
    
    for idx, product in enumerate(products, 1):
        product_id = product['id']
        image_urls = product['images'][:MAX_IMAGES_PER_PRODUCT]
        
        print(f"[{idx}/{len(products)}] {product['name']} (ID: {product_id})")
        
        if not image_urls:
            print(f"    ⚠ No images available")
            product['local_images'] = []
            product['primary_image'] = None
            continue
        
        local_images = []
        
        for img_idx, url in enumerate(image_urls, 1):
            filename = f"{product_id}_{img_idx}.jpg"
            save_path = IMAGES_DIR / filename
            
            # Skip if already downloaded
            if save_path.exists():
                print(f"    ✓ Image {img_idx} already exists")
                local_images.append(f"/images/products/{filename}")
                stats['total_images_downloaded'] += 1
                continue
            
            # Download image
            print(f"    ⬇ Downloading image {img_idx}...")
            success = download_image(url, save_path)
            
            if success:
                local_images.append(f"/images/products/{filename}")
                stats['total_images_downloaded'] += 1
                print(f"    ✓ Saved: {filename}")
                time.sleep(DELAY_BETWEEN_DOWNLOADS)
            else:
                stats['total_images_failed'] += 1
                print(f"    ✗ Failed to download")
        
        # Update product with local paths
        product['local_images'] = local_images
        product['primary_image'] = local_images[0] if local_images else None
        
        if local_images:
            stats['products_with_images'] += 1
        
        print()
    
    # Print statistics
    print(f"{'='*60}")
    print(f"DOWNLOAD SUMMARY")
    print(f"{'='*60}\n")
    print(f"Products processed: {stats['total_products']}")
    print(f"Products with images: {stats['products_with_images']} ({stats['products_with_images']/stats['total_products']*100:.1f}%)")
    print(f"Images downloaded: {stats['total_images_downloaded']}")
    print(f"Images failed: {stats['total_images_failed']}")
    print()
    
    return products


def save_products_json(products):
    """Save updated product data as JSON."""
    # Add embedding placeholders
    for idx, product in enumerate(products):
        product['embeddings'] = {
            'text_index': idx,
            'image_index': idx,
            'qdrant_id': f"prod_{product['id']}"
        }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved products.json to: {OUTPUT_JSON.absolute()}")
    print(f"  Total products: {len(products)}")


def create_frontend_symlink():
    """Create symlink in Frontend/public/images/products pointing to Data/raw/images."""
    frontend_images = Path("../../Frontend/public/images/products")
    
    # Create parent directory if needed
    frontend_images.parent.mkdir(parents=True, exist_ok=True)
    
    # Create symlink or copy notice
    if not frontend_images.exists():
        try:
            # Try creating symlink (requires admin on Windows)
            target = IMAGES_DIR.absolute()
            frontend_images.symlink_to(target, target_is_directory=True)
            print(f"\n✓ Created symlink: {frontend_images} → {target}")
        except OSError:
            print(f"\n⚠ Could not create symlink (needs admin privileges)")
            print(f"  Manual step: Copy or link {IMAGES_DIR.absolute()}")
            print(f"  To: {frontend_images.absolute()}")
            print(f"\n  Or run as admin:")
            print(f"  mklink /D \"{frontend_images.absolute()}\" \"{IMAGES_DIR.absolute()}\"")
    else:
        print(f"\n✓ Frontend images path already exists: {frontend_images}")


def main():
    print("\n" + "="*60)
    print("FURNIVERSE IMAGE DOWNLOADER")
    print("="*60)
    
    # Check if CSV exists
    if not INPUT_CSV.exists():
        print(f"\n✗ Error: {INPUT_CSV} not found!")
        print(f"  Make sure products.csv exists in Data/processed/")
        return
    
    # Load products
    print(f"\n⬇ Loading products from {INPUT_CSV}...")
    products = load_products_from_csv()
    print(f"✓ Loaded {len(products)} products")
    
    # Download images
    products = download_product_images(products)
    
    # Save updated JSON
    print(f"\n{'='*60}")
    print(f"SAVING PRODUCTS.JSON")
    print(f"{'='*60}\n")
    save_products_json(products)
    
    # Create frontend symlink
    create_frontend_symlink()
    
    print(f"\n{'='*60}")
    print("✓ COMPLETE")
    print(f"{'='*60}\n")
    print("Next steps:")
    print("1. Check images in: Data/raw/images/")
    print("2. Verify products.json in: Data/processed/")
    print("3. Run embedding generation with local images")
    print()


if __name__ == "__main__":
    main()

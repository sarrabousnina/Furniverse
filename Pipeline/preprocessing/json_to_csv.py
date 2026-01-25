"""
Convert products.json to CSV for easier analysis and processing.
Usage: python json_to_csv.py
"""

import json
import csv
import os
from pathlib import Path


def flatten_product(product):
    """Flatten nested product structure for CSV"""
    flat = {
        'id': product.get('id'),
        'name': product.get('name'),
        'category': product.get('category'),
        'price': product.get('price'),
        'rating': product.get('rating'),
        'reviewCount': product.get('reviewCount'),
        'image': product.get('image'),
        'description': product.get('description'),
        'inStock': product.get('inStock'),
        'trending': product.get('trending'),
        
        # Dimensions
        'width': product.get('dimensions', {}).get('width'),
        'height': product.get('dimensions', {}).get('height'),
        'depth': product.get('dimensions', {}).get('depth'),
        
        # Arrays as comma-separated strings
        'images': '|'.join(product.get('images', [])),
        'features': '|'.join(product.get('features', [])),
        'styles': ','.join(product.get('styles', [])),
        'colors': ','.join(product.get('colors', [])),
        'tags': ','.join(product.get('tags', [])),
    }
    return flat


def main():
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    input_path = project_root / 'Data' / 'raw' / 'products.json'
    output_path = project_root / 'Data' / 'processed' / 'products.csv'
    
    print(f"Reading from: {input_path}")
    
    # Load JSON
    with open(input_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Loaded {len(products)} products")
    
    # Flatten and write CSV
    if products:
        fieldnames = flatten_product(products[0]).keys()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in products:
                writer.writerow(flatten_product(product))
        
        print(f"✓ Saved to: {output_path}")
        print(f"  Columns: {len(fieldnames)}")
        print(f"  Rows: {len(products)}")
    else:
        print("⚠ No products found")


if __name__ == '__main__':
    main()

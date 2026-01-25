import argparse
import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup


def _read_file_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _fetch_url(url: str, timeout: int = 30) -> str:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    })
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def _extract_meta(soup: BeautifulSoup) -> Dict[str, str]:
    meta: Dict[str, str] = {}
    canon = soup.find("link", rel="canonical")
    if canon and canon.get("href"):
        meta["canonical"] = canon.get("href")
    for name in ("og:title", "og:description", "og:image", "og:url", "og:site_name"):
        tag = soup.find("meta", property=name)
        if tag and tag.get("content"):
            meta[name] = tag.get("content")
    for name in ("description", "keywords"):
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            meta[name] = tag.get("content")
    return meta


def _parse_json(text: str) -> Optional[Any]:
    try:
        return json.loads(text)
    except Exception:
        return None


def _extract_json_ld_product(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    primary = soup.find("script", id=re.compile("pip-range-json-ld"), type="application/ld+json")
    candidates: List[str] = []
    if primary and primary.string:
        candidates.append(primary.string)
    for s in soup.find_all("script", type="application/ld+json"):
        if s == primary:
            continue
        if s.string:
            candidates.append(s.string)
    for raw in candidates:
        data = _parse_json(raw)
        if data is None:
            continue
        if isinstance(data, dict) and (data.get("@type") == "Product" or data.get("type") == "Product"):
            return data
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and (item.get("@type") == "Product" or item.get("type") == "Product"):
                    return item
    return None


def _extract_utag_data(html: str) -> Optional[Dict[str, Any]]:
    m = re.search(r"var\s+utag_data\s*=\s*(\{.*?\});", html, flags=re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    raw = raw.replace("\u003e", ">")
    return _parse_json(raw)


def _parse_dimension(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        try:
            return float(value)
        except Exception:
            return 0.0
    s = str(value)
    s = s.replace("\u2033", "").replace("″", "").replace('"', "").strip()
    parts = s.split()
    try:
        if len(parts) == 2 and "/" in parts[1]:
            whole = float(parts[0])
            num, den = parts[1].split("/")
            return whole + (float(num) / float(den))
        if len(parts) == 1:
            return float(parts[0])
    except Exception:
        return 0.0
    return 0.0


def _infer_styles(name: str, description: str, category: str) -> List[str]:
    text = f"{name} {description} {category}".lower()
    styles: Dict[str, List[str]] = {
        "Modern": ["modern", "contemporary", "minimalist", "sleek"],
        "Scandinavian": ["scandinavian", "nordic", "simple", "functional"],
        "Traditional": ["traditional", "classic", "vintage", "timeless"],
        "Industrial": ["industrial", "metal", "steel", "urban"],
        "Rustic": ["rustic", "wood", "natural", "farmhouse"],
        "Minimalist": ["minimalist", "clean", "simple", "minimal"],
        "Glam": ["velvet", "luxury", "elegant", "glamorous"],
    }
    found = [style for style, kws in styles.items() if any(k in text for k in kws)]
    return found or ["Modern"]


def _colors_from_name(name: str) -> List[str]:
    palette = [
        "white", "black", "gray", "grey", "beige", "brown", "blue", "navy",
        "green", "emerald", "red", "pink", "yellow", "orange", "purple",
        "natural", "oak", "walnut", "birch", "dark", "light",
    ]
    n = name.lower()
    colors = [c for c in palette if c in n]
    return colors or ["natural"]


def _tags_from_text(name: str, description: str, price: float) -> List[str]:
    text = f"{name} {description}".lower()
    tags: List[str] = []
    if price > 0:
        if price < 200:
            tags.append("affordable")
        elif price > 1000:
            tags.append("luxury")
    tag_kws: Dict[str, List[str]] = {
        "comfortable": ["comfortable", "comfy", "cozy"],
        "compact": ["compact", "small", "space-saving"],
        "spacious": ["spacious", "large", "roomy"],
        "durable": ["durable", "sturdy", "strong"],
        "elegant": ["elegant", "sophisticated", "refined"],
        "functional": ["functional", "practical", "versatile"],
        "minimalist": ["minimalist", "simple", "clean"],
        "statement-piece": ["statement", "bold", "eye-catching"],
    }
    for tag, kws in tag_kws.items():
        if any(k in text for k in kws):
            tags.append(tag)
    return (tags[:6] or ["stylish", "functional"])


def _features_from_description(description: str) -> List[str]:
    sentences = [s.strip() for s in re.split(r"[.!]\s+", description) if s.strip()]
    feats = [s for s in sentences if len(s) > 10][:5]
    return feats or ["Quality construction", "Easy to assemble", "Durable materials", "Functional design"]


def _sanitize_images(images: List[str]) -> List[str]:
    def ok(url: str) -> bool:
        u = url.lower()
        return (u.endswith(".jpg") or u.endswith(".jpeg") or "/images/products/" in u) and ("pixel" not in u and "cdn-cgi" not in u)

    out: List[str] = []
    for img in images:
        if isinstance(img, dict):
            val = img.get("contentUrl") or img.get("url") or ""
        else:
            val = str(img)
        if val and ok(val):
            out.append(val)
    return out


def build_product(url: Optional[str], soup: BeautifulSoup, html: str) -> Dict[str, Any]:
    json_ld = _extract_json_ld_product(soup)
    utag = _extract_utag_data(html)
    meta = _extract_meta(soup)

    raw_name = (json_ld or {}).get("name") or meta.get("og:title") or meta.get("description") or "Unknown Product"
    # Clean name: remove brand prefixes and extra formatting
    name = raw_name.replace("IKEA ", "").replace(" - IKEA", "").strip()
    if " - " in name:
        name = name.split(" - ")[0].strip()
    
    description = (json_ld or {}).get("description") or meta.get("description") or meta.get("og:description") or ""
    category = (json_ld or {}).get("category") or (utag or {}).get("category_local") or (utag or {}).get("hfb_name") or "Furniture"

    offers = (json_ld or {}).get("offers") or {}
    price = int(float(offers.get("price", 0) or 0))

    agg = (json_ld or {}).get("aggregateRating") or {}
    rating = float(agg.get("ratingValue", 0) or 0)
    review_count = int(agg.get("reviewCount", 0) or 0)

    images_raw = (json_ld or {}).get("image") or []
    images = _sanitize_images(images_raw if isinstance(images_raw, list) else [images_raw])
    if not images and meta.get("og:image"):
        images = _sanitize_images([meta["og:image"]])
    image = images[0] if images else ""

    # Parse dimensions - height might be in different JSON-LD fields
    width = _parse_dimension((json_ld or {}).get("width"))
    height = _parse_dimension((json_ld or {}).get("height"))
    depth = _parse_dimension((json_ld or {}).get("depth"))
    
    # If height is 0, try to estimate from width (typical sofa proportions)
    if height == 0 and width > 0:
        height = int(width * 0.4)  # Rough estimate
    
    dimensions = {
        "width": int(width),
        "height": int(height),
        "depth": int(depth)
    }

    availability = str(offers.get("availability", ""))
    in_stock = "instock" in availability.lower()

    sku_raw = (json_ld or {}).get("sku") or ((utag or {}).get("product_ids") or [""])[0]
    # Convert SKU like "405.959.42" to numeric ID
    product_id = int(sku_raw.replace(".", "")) if sku_raw else 1

    styles = _infer_styles(name, description, category)
    colors = _colors_from_name(name)
    tags = _tags_from_text(name, description, price)
    features = _features_from_description(description)
    
    # Simple trending logic: high rating + many reviews
    trending = rating >= 4.0 and review_count >= 50

    return {
        "id": product_id,
        "name": name,
        "category": category,
        "price": price,
        "rating": rating,
        "reviewCount": review_count,
        "image": image,
        "images": images,
        "description": description,
        "features": features,
        "styles": styles,
        "colors": colors,
        "tags": tags,
        "dimensions": dimensions,
        "inStock": in_stock,
        "trending": trending,
    }


def extract_category_urls(html: str, base_url: str = "https://www.ikea.com") -> List[tuple]:
    """Extract all category URLs from IKEA's products page"""
    soup = BeautifulSoup(html, "html.parser")
    categories = []
    seen = set()
    
    # Find category links - IKEA uses /cat/ for category pages
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "/cat/" in href and href not in seen:
            full_url = href if href.startswith("http") else (base_url + href if not href.startswith("/") else base_url + href)
            # Extract category name from URL
            cat_name = href.split("/cat/")[-1].split("/")[0] if "/cat/" in href else "unknown"
            if full_url not in seen:
                seen.add(full_url)
                categories.append((cat_name, full_url))
    
    return categories


def extract_product_urls(html: str, base_url: str = "https://www.ikea.com") -> List[str]:
    """Extract product URLs from a category/listing page"""
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    
    # Find product links - IKEA uses /p/ for product pages
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "/p/" in href and href not in urls:
            if href.startswith("http"):
                urls.append(href)
            else:
                urls.append(base_url + href if not href.startswith("/") else base_url + href)
    
    # Deduplicate and filter
    seen = set()
    unique = []
    for url in urls:
        if url not in seen and "/p/" in url:
            seen.add(url)
            unique.append(url)
    
    return unique


def save_output(products: List[Dict[str, Any]], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="IKEA Product Scraper (JSON-LD + utag_data)")
    parser.add_argument("--url", help="Product page URL to fetch", default=None)
    parser.add_argument("--file", help="Path to local HTML file to parse", default=None)
    parser.add_argument("--category", help="Category page URL to scrape all products", default=None)
    parser.add_argument("--all", help="Scrape ALL categories and products", action="store_true")
    parser.add_argument("--out", help="Output JSON path", default="../Data/raw/products.json")
    parser.add_argument("--max", help="Maximum products to scrape per category", type=int, default=None)
    args = parser.parse_args()

    products = []

    if args.all:
        print("=" * 80)
        print("IKEA MASS SCRAPER - ALL CATEGORIES")
        print("=" * 80)
        
        # Hardcoded main categories - IKEA's primary furniture/home categories
        main_categories = [
            ("sofas", "https://www.ikea.com/us/en/cat/sofas-fu003/"),
            ("beds", "https://www.ikea.com/us/en/cat/beds-bm003/"),
            ("tables", "https://www.ikea.com/us/en/cat/tables-desks-fu004/"),
            ("chairs", "https://www.ikea.com/us/en/cat/chairs-fu002/"),
            ("storage", "https://www.ikea.com/us/en/cat/storage-furniture-st001/"),
            ("bookcases", "https://www.ikea.com/us/en/cat/bookcases-shelving-units-st002/"),
            ("tv-media", "https://www.ikea.com/us/en/cat/tv-media-furniture-10475/"),
            ("lighting", "https://www.ikea.com/us/en/cat/lighting-li001/"),
            ("textiles", "https://www.ikea.com/us/en/cat/textiles-rugs-10659/"),
            ("decoration", "https://www.ikea.com/us/en/cat/decoration-de001/"),
        ]
        
        total_products = 0
        
        for cat_name, cat_url in main_categories:
            print(f"\n{'='*80}")
            print(f"CATEGORY: {cat_name.upper()}")
            print(f"{'='*80}")
            
            try:
                print(f"Fetching category page: {cat_url}")
                html = _fetch_url(cat_url)
                product_urls = extract_product_urls(html)
                print(f"Found {len(product_urls)} products in {cat_name}")
                
                if args.max:
                    product_urls = product_urls[:args.max]
                    print(f"Limiting to {args.max} products")
                
                for idx, url in enumerate(product_urls, 1):
                    try:
                        print(f"[{idx}/{len(product_urls)}] {url}")
                        html = _fetch_url(url)
                        soup = BeautifulSoup(html, "html.parser")
                        product = build_product(url, soup, html)
                        products.append(product)
                        total_products += 1
                        print(f"  ✓ {product['name']} - ${product['price']}")
                    except Exception as e:
                        print(f"  ✗ Error: {e}")
                        continue
                        
                print(f"\n✓ Scraped {idx} products from {cat_name}")
                
            except Exception as e:
                print(f"✗ Failed to scrape category {cat_name}: {e}")
                continue
        
        print(f"\n{'='*80}")
        print(f"TOTAL: {total_products} products across {len(main_categories)} categories")
        print(f"{'='*80}")
        
    elif args.category:
        print(f"Fetching category page: {args.category}")
        html = _fetch_url(args.category)
        product_urls = extract_product_urls(html)
        print(f"Found {len(product_urls)} product URLs")
        
        if args.max:
            product_urls = product_urls[:args.max]
        
        for idx, url in enumerate(product_urls, 1):
            try:
                print(f"[{idx}/{len(product_urls)}] Scraping: {url}")
                html = _fetch_url(url)
                soup = BeautifulSoup(html, "html.parser")
                product = build_product(url, soup, html)
                products.append(product)
                print(f"  ✓ {product['name']} - ${product['price']}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
    elif args.file:
        html = _read_file_text(args.file)
        soup = BeautifulSoup(html, "html.parser")
        product = build_product(None, soup, html)
        products.append(product)
    elif args.url:
        html = _fetch_url(args.url)
        soup = BeautifulSoup(html, "html.parser")
        product = build_product(args.url, soup, html)
        products.append(product)
    else:
        print("No arguments provided. Use --all for mass scraping or --category for specific category.")
        return

    save_output(products, args.out)
    print(f"\n✓ Saved {len(products)} products to: {args.out}")


if __name__ == "__main__":
    main()

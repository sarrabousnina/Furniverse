"""
Color Palette Extraction for Furniverse

Extracts dominant colors from product images in both RGB and HSV color spaces.
Used for color-based product similarity and filtering.

Features:
- Dominant color extraction using K-means clustering
- RGB color features (red, green, blue channels)
- HSV color features (hue, saturation, value)
- Color histogram features
- Color palette generation
"""

import numpy as np
from typing import List, Dict, Tuple, Union
from PIL import Image
import requests
from io import BytesIO
import colorsys


class ColorExtractor:
    """Extract color features from product images"""
    
    def __init__(self, n_colors: int = 5, img_size: int = 150):
        """
        Initialize color extractor.
        
        Args:
            n_colors: Number of dominant colors to extract
            img_size: Image resize dimension for faster processing
        """
        self.n_colors = n_colors
        self.img_size = img_size
    
    def load_image(self, image_source: Union[str, Image.Image]) -> Image.Image:
        """
        Load image from URL, file path, or PIL Image.
        
        Args:
            image_source: URL, file path, or PIL Image
        
        Returns:
            PIL Image in RGB mode
        """
        if isinstance(image_source, Image.Image):
            return image_source.convert('RGB')
        
        if isinstance(image_source, str):
            if image_source.startswith('http'):
                response = requests.get(image_source, timeout=10)
                return Image.open(BytesIO(response.content)).convert('RGB')
            else:
                return Image.open(image_source).convert('RGB')
        
        raise ValueError(f"Unsupported image source type: {type(image_source)}")
    
    def extract_dominant_colors(self, image: Image.Image) -> np.ndarray:
        """
        Extract dominant colors using K-means clustering.
        
        Args:
            image: PIL Image
        
        Returns:
            Array of shape (n_colors, 3) with RGB values [0-255]
        """
        # Resize for faster processing
        img = image.resize((self.img_size, self.img_size))
        
        # Convert to numpy array and reshape to 2D
        pixels = np.array(img).reshape(-1, 3)
        
        # Remove very dark pixels (likely background)
        mask = pixels.sum(axis=1) > 30
        pixels = pixels[mask]
        
        if len(pixels) == 0:
            # Fallback if all pixels removed
            pixels = np.array(img).reshape(-1, 3)
        
        # K-means clustering
        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=self.n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_
        except ImportError:
            # Fallback: use random sampling if sklearn not available
            indices = np.random.choice(len(pixels), self.n_colors, replace=False)
            colors = pixels[indices]
        
        return colors.astype(np.uint8)
    
    def rgb_to_hsv(self, rgb: np.ndarray) -> np.ndarray:
        """
        Convert RGB colors to HSV.
        
        Args:
            rgb: Array of shape (n, 3) with RGB values [0-255]
        
        Returns:
            Array of shape (n, 3) with HSV values [0-1]
        """
        rgb_normalized = rgb / 255.0
        hsv = np.array([colorsys.rgb_to_hsv(*color) for color in rgb_normalized])
        return hsv
    
    def extract_color_histogram(self, image: Image.Image, bins: int = 8) -> np.ndarray:
        """
        Extract color histogram features.
        
        Args:
            image: PIL Image
            bins: Number of bins per channel
        
        Returns:
            Flattened histogram (bins^3 dimensions)
        """
        img = image.resize((self.img_size, self.img_size))
        pixels = np.array(img)
        
        hist, _ = np.histogramdd(
            pixels.reshape(-1, 3),
            bins=(bins, bins, bins),
            range=((0, 256), (0, 256), (0, 256))
        )
        
        # Normalize
        hist = hist.flatten()
        hist = hist / (hist.sum() + 1e-7)
        
        return hist
    
    def extract_features(self, image_source: Union[str, Image.Image]) -> Dict[str, np.ndarray]:
        """
        Extract all color features from an image.
        
        Args:
            image_source: Image URL, path, or PIL Image
        
        Returns:
            Dictionary with color features:
            - dominant_colors_rgb: (n_colors, 3) RGB values
            - dominant_colors_hsv: (n_colors, 3) HSV values
            - avg_rgb: (3,) average RGB color
            - avg_hsv: (3,) average HSV color
            - color_histogram: (bins^3,) color distribution
            - color_vector: (n_colors * 6 + 6 + histogram_size,) combined feature vector
        """
        image = self.load_image(image_source)
        
        # Extract dominant colors
        dominant_rgb = self.extract_dominant_colors(image)
        dominant_hsv = self.rgb_to_hsv(dominant_rgb)
        
        # Calculate averages
        avg_rgb = dominant_rgb.mean(axis=0)
        avg_hsv = dominant_hsv.mean(axis=0)
        
        # Extract histogram
        histogram = self.extract_color_histogram(image)
        
        # Combine into single feature vector
        # [dominant_rgb_flat, dominant_hsv_flat, avg_rgb, avg_hsv, histogram]
        color_vector = np.concatenate([
            dominant_rgb.flatten() / 255.0,  # Normalize to [0, 1]
            dominant_hsv.flatten(),
            avg_rgb / 255.0,
            avg_hsv,
            histogram
        ])
        
        return {
            'dominant_colors_rgb': dominant_rgb,
            'dominant_colors_hsv': dominant_hsv,
            'avg_rgb': avg_rgb,
            'avg_hsv': avg_hsv,
            'color_histogram': histogram,
            'color_vector': color_vector,
            'color_vector_dim': len(color_vector)
        }
    
    def get_color_palette_dict(self, image_source: Union[str, Image.Image]) -> Dict[str, List]:
        """
        Get color palette as dictionary (for JSON serialization).
        
        Args:
            image_source: Image URL, path, or PIL Image
        
        Returns:
            Dictionary with color palette information
        """
        features = self.extract_features(image_source)
        
        return {
            'dominant_colors_rgb': features['dominant_colors_rgb'].tolist(),
            'dominant_colors_hsv': features['dominant_colors_hsv'].tolist(),
            'avg_rgb': features['avg_rgb'].tolist(),
            'avg_hsv': features['avg_hsv'].tolist(),
            'color_names': self._rgb_to_color_names(features['dominant_colors_rgb'])
        }
    
    def _rgb_to_color_names(self, rgb_colors: np.ndarray) -> List[str]:
        """
        Convert RGB values to human-readable color names.
        
        Args:
            rgb_colors: Array of RGB values
        
        Returns:
            List of color names
        """
        color_map = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray': (128, 128, 128),
            'orange': (255, 165, 0),
            'brown': (165, 42, 42),
            'beige': (245, 245, 220),
            'pink': (255, 192, 203),
            'purple': (128, 0, 128)
        }
        
        names = []
        for rgb in rgb_colors:
            min_dist = float('inf')
            closest_name = 'unknown'
            
            for name, ref_rgb in color_map.items():
                dist = np.linalg.norm(rgb - np.array(ref_rgb))
                if dist < min_dist:
                    min_dist = dist
                    closest_name = name
            
            names.append(closest_name)
        
        return names


# ============================================================================
# Convenience Functions
# ============================================================================

def extract_product_color_features(product: Dict, extractor: ColorExtractor = None) -> Dict:
    """
    Extract color features for a product.
    
    Args:
        product: Product dictionary with 'image' or 'primary_image' field
        extractor: ColorExtractor instance (creates new one if None)
    
    Returns:
        Color features dictionary
    """
    if extractor is None:
        extractor = ColorExtractor()
    
    # Get image URL or path
    image_source = product.get('primary_image') or product.get('image')
    
    if not image_source:
        raise ValueError(f"Product {product.get('id')} has no image")
    
    # Handle local image paths
    if isinstance(image_source, str) and image_source.startswith('/'):
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        # Remove '/images/products/' prefix since we're adding 'Data/raw/images'
        image_path = image_source.lstrip('/')
        if image_path.startswith('images/products/'):
            image_path = image_path[len('images/products/'):]
        image_source = str(project_root / 'Data' / 'raw' / 'images' / image_path)
    
    try:
        return extractor.extract_features(image_source)
    except Exception as e:
        print(f"⚠ Failed to extract colors for product {product.get('id')}: {e}")
        # Return zero vector as fallback
        return {
            'color_vector': np.zeros(extractor.n_colors * 6 + 6 + 512),
            'color_vector_dim': extractor.n_colors * 6 + 6 + 512
        }


if __name__ == '__main__':
    # Test color extraction
    print("Testing Color Extractor...")
    
    extractor = ColorExtractor(n_colors=5)
    
    # Test with a sample product
    test_product = {
        'id': 'test',
        'image': 'https://www.ikea.com/us/en/images/products/glostad-sofa-knisa-dark-gray__1234948_pe917261_s5.jpg'
    }
    
    try:
        features = extract_product_color_features(test_product, extractor)
        print(f"✓ Extracted color vector: {features['color_vector'].shape}")
        print(f"✓ Color vector dimension: {features['color_vector_dim']}")
        
        palette = extractor.get_color_palette_dict(test_product['image'])
        print(f"✓ Dominant colors: {palette['color_names']}")
        print(f"✓ Avg RGB: {palette['avg_rgb']}")
    except Exception as e:
        print(f"✗ Error: {e}")

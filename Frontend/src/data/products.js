// Mock product data for Furniverse e-commerce
export const PRODUCTS = [
  // Sofas
  {
    id: 1,
    name: 'Modern Velvet Sofa',
    category: 'Sofas',
    price: 1499,
    rating: 4.8,
    reviewCount: 234,
    image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=800&h=600&fit=crop',
    ],
    description: 'Luxurious velvet sofa with deep emerald upholstery. Features premium cushioning and a sturdy wooden frame. Perfect for modern and contemporary interiors.',
    features: ['Premium velvet fabric', 'Kiln-dried hardwood frame', 'High-density foam cushions', 'Stain-resistant treatment'],
    styles: ['Modern', 'Glam'],
    colors: ['emerald', 'navy', 'gray'],
    tags: ['velvet', 'luxury', 'statement-piece'],
    inStock: true,
    trending: true,
  },
  {
    id: 2,
    name: 'Scandinavian Sectional',
    category: 'Sofas',
    price: 2199,
    rating: 4.9,
    reviewCount: 189,
    image: 'https://images.unsplash.com/photo-1550226891-ef816aed4a98?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1550226891-ef816aed4a98?w=800&h=600&fit=crop',
    ],
    description: 'Clean-lined sectional sofa in light gray fabric. Modular design allows multiple configurations. Ideal for open living spaces.',
    features: ['Modular design', 'Removable cushion covers', 'Solid wood legs', 'Eco-friendly materials'],
    styles: ['Scandinavian', 'Minimalist'],
    colors: ['gray', 'beige'],
    tags: ['modular', 'versatile', 'family-friendly'],
    inStock: true,
    trending: true,
  },
  {
    id: 3,
    name: 'Mid-Century Loveseat',
    category: 'Sofas',
    price: 899,
    rating: 4.6,
    reviewCount: 156,
    image: 'https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=800&h=600&fit=crop',
    ],
    description: 'Classic mid-century design with tapered wooden legs and warm walnut finish. Compact size perfect for apartments.',
    features: ['Walnut wood base', 'Premium fabric upholstery', 'Pocket coil cushions', 'Hand-finished details'],
    styles: ['Mid-Century', 'Rustic'],
    colors: ['walnut', 'cream'],
    tags: ['compact', 'retro', 'apartment-friendly'],
    inStock: true,
  },

  // Tables
  {
    id: 4,
    name: 'Marble Coffee Table',
    category: 'Tables',
    price: 799,
    rating: 4.7,
    reviewCount: 312,
    image: 'https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=800&h=600&fit=crop',
    ],
    description: 'Stunning marble top coffee table with brass legs. The perfect centerpiece for any modern living room.',
    features: ['Carrara marble top', 'Brushed brass legs', 'Protective coating', 'Easy assembly'],
    styles: ['Modern', 'Glam'],
    colors: ['white', 'gold'],
    tags: ['luxury', 'statement', 'marble'],
    inStock: true,
    trending: true,
  },
  {
    id: 5,
    name: 'Industrial Dining Table',
    category: 'Tables',
    price: 1299,
    rating: 4.8,
    reviewCount: 198,
    image: 'https://images.unsplash.com/photo-1617104678098-ab8fc7a4e682?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1617104678098-ab8fc7a4e682?w=800&h=600&fit=crop',
    ],
    description: 'Reclaimed wood dining table with iron pipe base. Seats 8 comfortably. Perfect for industrial and rustic spaces.',
    features: ['Reclaimed wood top', 'Wrought iron base', 'Seats 8', 'Natural finish'],
    styles: ['Industrial', 'Rustic'],
    colors: ['brown', 'black'],
    tags: ['rustic', 'large', 'dining'],
    inStock: true,
  },
  {
    id: 6,
    name: 'Minimalist Side Table',
    category: 'Tables',
    price: 249,
    rating: 4.5,
    reviewCount: 267,
    image: 'https://images.unsplash.com/photo-1499933374294-4584851497cc?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1499933374294-4584851497cc?w=800&h=600&fit=crop',
    ],
    description: 'Simple and elegant round side table. Matte black finish with hidden storage compartment.',
    features: ['Hidden storage', 'Matte black finish', 'Sturdy construction', 'Easy to move'],
    styles: ['Minimalist', 'Modern'],
    colors: ['black'],
    tags: ['compact', 'storage', 'versatile'],
    inStock: true,
  },

  // Lamps
  {
    id: 7,
    name: 'Arched Floor Lamp',
    category: 'Lamps',
    price: 349,
    rating: 4.6,
    reviewCount: 423,
    image: 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&h=600&fit=crop',
    ],
    description: 'Elegant arched floor lamp with marble base. Adjustable height and dimmable LED bulb included.',
    features: ['Marble base', 'Adjustable height', 'LED bulb included', 'Brushed steel finish'],
    styles: ['Modern', 'Minimalist'],
    colors: ['brass', 'chrome'],
    tags: ['adjustable', 'led', 'modern'],
    inStock: true,
    trending: true,
  },
  {
    id: 8,
    name: 'Boho Table Lamp Set',
    category: 'Lamps',
    price: 189,
    rating: 4.7,
    reviewCount: 289,
    image: 'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800&h=600&fit=crop',
    ],
    description: 'Set of 2 bohemian-inspired table lamps with ceramic bases and fabric shades. Warm ambient lighting.',
    features: ['Set of 2', 'Hand-painted ceramic', 'Fabric shades', 'E26 base'],
    styles: ['Bohemian', 'Rustic'],
    colors: ['terracotta', 'cream'],
    tags: ['boho', 'set', 'warm-lighting'],
    inStock: true,
  },
  {
    id: 9,
    name: 'Brass Wall Sconce',
    category: 'Lamps',
    price: 129,
    rating: 4.4,
    reviewCount: 167,
    image: 'https://images.unsplash.com/photo-1540932296774-3bedde00830c?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1540932296774-3bedde00830c?w=800&h=600&fit=crop',
    ],
    description: 'Vintage-inspired brass wall sconce with swing arm. Perfect for bedside or reading nooks.',
    features: ['Swing arm design', 'Antique brass finish', 'Hardwired', 'UL listed'],
    styles: ['Mid-Century', 'Industrial'],
    colors: ['brass'],
    tags: ['wall-mount', 'vintage', 'reading'],
    inStock: true,
  },

  // Chairs
  {
    id: 10,
    name: 'Eames-Style Lounge Chair',
    category: 'Chairs',
    price: 899,
    rating: 4.9,
    reviewCount: 534,
    image: 'https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=800&h=600&fit=crop',
    ],
    description: 'Iconic mid-century lounge chair with molded plywood shell and premium leather cushions. Ottoman included.',
    features: ['Molded plywood shell', 'Genuine leather cushions', 'Ottoman included', '7-position tilt'],
    styles: ['Mid-Century', 'Modern'],
    colors: ['walnut', 'black'],
    tags: ['iconic', 'luxury', 'comfortable'],
    inStock: true,
    trending: true,
  },
  {
    id: 11,
    name: 'Velvet Accent Chair',
    category: 'Chairs',
    price: 549,
    rating: 4.7,
    reviewCount: 278,
    image: 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=800&h=600&fit=crop',
    ],
    description: 'Plush velvet accent chair with gold tapered legs. Channel tufting adds sophisticated elegance.',
    features: ['Channel tufting', 'Gold legs', 'High-back design', 'Removable seat cushion'],
    styles: ['Glam', 'Modern'],
    colors: ['navy', 'emerald', 'pink'],
    tags: ['accent', 'velvet', 'luxury'],
    inStock: true,
  },
  {
    id: 12,
    name: 'Scandinavian Dining Chair',
    category: 'Chairs',
    price: 199,
    rating: 4.6,
    reviewCount: 445,
    image: 'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=800&h=600&fit=crop',
    ],
    description: 'Simple and functional dining chair with curved backrest. Light wood finish with beige fabric seat.',
    features: ['Ergonomic design', 'Solid wood construction', 'Easy to clean', 'Stackable'],
    styles: ['Scandinavian', 'Minimalist'],
    colors: ['natural', 'white'],
    tags: ['dining', 'comfortable', 'stackable'],
    inStock: true,
  },
  {
    id: 13,
    name: 'Leather Club Chair',
    category: 'Chairs',
    price: 799,
    rating: 4.8,
    reviewCount: 201,
    image: 'https://images.unsplash.com/photo-1565538810643-b5bdb714032a?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1565538810643-b5bdb714032a?w=600&h=400&fit=crop',
    ],
    description: 'Classic leather club chair with nailhead trim. Deep seating for ultimate comfort. Perfect for reading corners.',
    features: ['Top-grain leather', 'Nailhead trim', 'Kiln-dried frame', 'Down-blend cushions'],
    styles: ['Industrial', 'Mid-Century'],
    colors: ['brown', 'cognac'],
    tags: ['leather', 'classic', 'comfort'],
    inStock: true,
  },
];

export const CATEGORIES = [
  { id: 'all', name: 'All Products', icon: '🛋️' },
  { id: 'sofas', name: 'Sofas', icon: '🛋️' },
  { id: 'tables', name: 'Tables', icon: '🪵' },
  { id: 'lamps', name: 'Lamps', icon: '💡' },
  { id: 'chairs', name: 'Chairs', icon: '🪑' },
];

// Helper function to get products by category
export const getProductsByCategory = (category) => {
  if (category === 'all') return PRODUCTS;
  return PRODUCTS.filter(p => p.category.toLowerCase() === category);
};

// Helper function to search products
export const searchProducts = (query) => {
  const lowerQuery = query.toLowerCase();
  return PRODUCTS.filter(p =>
    p.name.toLowerCase().includes(lowerQuery) ||
    p.description.toLowerCase().includes(lowerQuery) ||
    p.tags.some(tag => tag.toLowerCase().includes(lowerQuery)) ||
    p.styles.some(style => style.toLowerCase().includes(lowerQuery))
  );
};

// Helper function to get trending products
export const getTrendingProducts = () => {
  return PRODUCTS.filter(p => p.trending);
};

// Helper function to get product by ID
export const getProductById = (id) => {
  return PRODUCTS.find(p => p.id === parseInt(id));
};

// Helper function to get related products
export const getRelatedProducts = (productId, limit = 4) => {
  const product = getProductById(productId);
  if (!product) return [];

  // Find products with same category or similar styles
  const related = PRODUCTS.filter(p =>
    p.id !== productId &&
    (p.category === product.category || p.styles.some(s => product.styles.includes(s)))
  );

  return related.slice(0, limit);
};

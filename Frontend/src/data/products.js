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
    dimensions: {
      width: 84,
      height: 34,
      depth: 36,
      seatHeight: 18
    },
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
    dimensions: {
      width: 110,
      height: 33,
      depth: 85,
      seatHeight: 17
    },
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
    dimensions: {
      width: 60,
      height: 32,
      depth: 34,
      seatHeight: 17
    },
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
    dimensions: {
      width: 48,
      height: 18,
      depth: 24
    },
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
    dimensions: {
      width: 72,
      height: 30,
      depth: 36
    },
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
    dimensions: {
      width: 20,
      height: 22,
      depth: 20
    },
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
    dimensions: {
      height: 68,
      diameter: 12
    },
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
    dimensions: {
      height: 24,
      diameter: 14
    },
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
    dimensions: {
      height: 12,
      width: 8,
      depth: 14
    },
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
    dimensions: {
      width: 33,
      height: 32,
      depth: 32,
      seatHeight: 17
    },
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
    dimensions: {
      width: 28,
      height: 34,
      depth: 30,
      seatHeight: 18
    },
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
    dimensions: {
      width: 22,
      height: 32,
      depth: 22,
      seatHeight: 18
    },
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
    dimensions: {
      width: 32,
      height: 34,
      depth: 34,
      seatHeight: 17
    },
    inStock: true,
  },

  // Additional Sofas
  {
    id: 14,
    name: 'Chesterfield Tufted Sofa',
    category: 'Sofas',
    price: 1899,
    rating: 4.9,
    reviewCount: 167,
    image: 'https://images.unsplash.com/photo-1550226891-ef816aed4a98?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1550226891-ef816aed4a98?w=800&h=600&fit=crop',
    ],
    description: 'Timeless Chesterfield design with deep button tufting. Premium leather upholstery with antique brass nailhead trim.',
    features: ['Deep button tufting', 'Top-grain leather', 'Antique brass trim', 'Handcrafted frame'],
    styles: ['Mid-Century', 'Industrial'],
    colors: ['brown', 'black', 'burgundy'],
    tags: ['classic', 'leather', 'tufted', 'statement-piece'],
    dimensions: {
      width: 88,
      height: 35,
      depth: 38,
      seatHeight: 18
    },
    inStock: true,
    trending: true,
  },
  {
    id: 15,
    name: 'Coastal Sleeper Sofa',
    category: 'Sofas',
    price: 1299,
    rating: 4.5,
    reviewCount: 143,
    image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&h=600&fit=crop',
    ],
    description: 'Versatile sleeper sofa with memory foam mattress. Light linen upholstery perfect for coastal and beach house styles.',
    features: ['Queen sleeper', 'Memory foam mattress', 'Removable cushions', 'Easy-pull mechanism'],
    styles: ['Coastal', 'Transitional'],
    colors: ['white', 'sand', 'blue'],
    tags: ['sleeper', 'guest-bed', 'linen', 'versatile'],
    dimensions: {
      width: 78,
      height: 35,
      depth: 40,
      seatHeight: 17
    },
    inStock: true,
  },
  {
    id: 16,
    name: 'Lawson Style Sofa',
    category: 'Sofas',
    price: 1099,
    rating: 4.6,
    reviewCount: 198,
    image: 'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=800&h=600&fit=crop',
    ],
    description: 'Classic Lawson design with rolled arms and loose back cushions. Performance fabric resists stains and fading.',
    features: ['Rolled arms', 'Performance fabric', 'Loose cushions', 'Kiln-dried frame'],
    styles: ['Transitional', 'Traditional'],
    colors: ['gray', 'navy', 'beige'],
    tags: ['family-friendly', 'durable', 'classic'],
    dimensions: {
      width: 92,
      height: 34,
      depth: 38,
      seatHeight: 18
    },
    inStock: true,
  },

  // Additional Tables
  {
    id: 17,
    name: 'Round Glass Dining Table',
    category: 'Tables',
    price: 899,
    rating: 4.7,
    reviewCount: 234,
    image: 'https://images.unsplash.com/photo-1617806118233-18e1de247200?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1617806118233-18e1de247200?w=800&h=600&fit=crop',
    ],
    description: 'Elegant round glass top table with pedestal base. Tempered glass with chrome finish. Seats 4 comfortably.',
    features: ['Tempered glass top', 'Chrome pedestal base', 'Seats 4', 'Easy assembly'],
    styles: ['Modern', 'Minimalist'],
    colors: ['clear', 'chrome'],
    tags: ['glass', 'round', 'modern', 'space-saving'],
    dimensions: {
      diameter: 48,
      height: 30
    },
    inStock: true,
  },
  {
    id: 18,
    name: 'Rustic Console Table',
    category: 'Tables',
    price: 449,
    rating: 4.5,
    reviewCount: 156,
    image: 'https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=800&h=600&fit=crop',
    ],
    description: 'Reclaimed wood console table with metal hairpin legs. Perfect entryway or hallway table with bottom shelf.',
    features: ['Reclaimed wood', 'Hairpin legs', 'Bottom shelf', '60 inches wide'],
    styles: ['Rustic', 'Industrial'],
    colors: ['brown', 'black'],
    tags: ['console', 'entryway', 'reclaimed-wood'],
    dimensions: {
      width: 60,
      height: 32,
      depth: 16
    },
    inStock: true,
  },
  {
    id: 19,
    name: 'Nesting Coffee Tables',
    category: 'Tables',
    price: 399,
    rating: 4.6,
    reviewCount: 287,
    image: 'https://images.unsplash.com/photo-1499933374294-4584851497cc?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1499933374294-4584851497cc?w=800&h=600&fit=crop',
    ],
    description: 'Set of 2 nesting tables with marble tops and gold frames. Versatile design can be used together or separately.',
    features: ['Set of 2', 'Faux marble tops', 'Gold metal frames', 'Nested design'],
    styles: ['Glam', 'Modern'],
    colors: ['white', 'gold'],
    tags: ['nesting', 'versatile', 'marble', 'set'],
    dimensions: {
      largeTable: {
        width: 32,
        height: 18,
        depth: 24
      },
      smallTable: {
        width: 24,
        height: 16,
        depth: 18
      }
    },
    inStock: true,
    trending: true,
  },

  // Additional Lamps
  {
    id: 20,
    name: 'Crystal Chandelier',
    category: 'Lamps',
    price: 599,
    rating: 4.8,
    reviewCount: 189,
    image: 'https://images.unsplash.com/photo-1540932296774-3bedde00830c?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1540932296774-3bedde00830c?w=800&h=600&fit=crop',
    ],
    description: 'Stunning crystal chandelier with draped crystals and chrome frame. Dimmable with adjustable chain length.',
    features: ['Genuine crystals', 'Chrome frame', 'Dimmable', 'Adjustable height'],
    styles: ['Glam', 'Modern'],
    colors: ['chrome', 'clear'],
    tags: ['chandelier', 'crystal', 'statement', 'luxury'],
    dimensions: {
      height: 28,
      diameter: 24
    },
    inStock: true,
  },
  {
    id: 21,
    name: 'Industrial Cage Pendant',
    category: 'Lamps',
    price: 159,
    rating: 4.5,
    reviewCount: 278,
    image: 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&h=600&fit=crop',
    ],
    description: 'Vintage-inspired cage pendant light with Edison bulb. Perfect for kitchen islands or dining areas.',
    features: ['Metal cage design', 'Edison bulb included', 'Adjustable cord', 'Hardwired'],
    styles: ['Industrial', 'Rustic'],
    colors: ['bronze', 'black', 'brass'],
    tags: ['pendant', 'edison', 'vintage', 'industrial'],
    dimensions: {
      height: 14,
      diameter: 10
    },
    inStock: true,
  },
  {
    id: 22,
    name: 'Modern Arc Lamp',
    category: 'Lamps',
    price: 279,
    rating: 4.6,
    reviewCount: 345,
    image: 'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800&h=600&fit=crop',
    ],
    description: 'Sleek arc floor lamp with marble base. Adjustable head and dimmer switch. Perfect for reading nooks.',
    features: ['Marble base', 'Adjustable head', 'Built-in dimmer', 'LED compatible'],
    styles: ['Modern', 'Minimalist'],
    colors: ['brass', 'black', 'chrome'],
    tags: ['arc-lamp', 'adjustable', 'modern', 'reading'],
    dimensions: {
      height: 64,
      diameter: 16
    },
    inStock: true,
  },

  // Additional Chairs
  {
    id: 23,
    name: 'Wingback Chair',
    category: 'Chairs',
    price: 699,
    rating: 4.8,
    reviewCount: 212,
    image: 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=800&h=600&fit=crop',
    ],
    description: 'Classic wingback chair with nailhead trim and exposed wood legs. Perfect accent piece for living room or bedroom.',
    features: ['Nailhead trim', 'Exposed wood frame', 'High-back design', 'Sinuous spring cushion'],
    styles: ['Traditional', 'Transitional'],
    colors: ['gray', 'navy', 'cream'],
    tags: ['wingback', 'classic', 'accent', 'comfortable'],
    dimensions: {
      width: 30,
      height: 42,
      depth: 36,
      seatHeight: 19
    },
    inStock: true,
  },
  {
    id: 24,
    name: 'Accent Bergère Chair',
    category: 'Chairs',
    price: 649,
    rating: 4.7,
    reviewCount: 167,
    image: 'https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=800&h=600&fit=crop',
    ],
    description: 'French-inspired Bergère chair with cane detailing and upholstered cushion. Elegant and timeless design.',
    features: ['Cane back detailing', 'Upholstered cushion', 'Carved wooden frame', 'Antique finish'],
    styles: ['Traditional', 'Rustic'],
    colors: ['cream', 'light-blue', 'gray'],
    tags: ['bergere', 'french', 'cane', 'elegant'],
    dimensions: {
      width: 28,
      height: 36,
      depth: 30,
      seatHeight: 18
    },
    inStock: true,
  },
  {
    id: 25,
    name: 'Barrel Chair',
    category: 'Chairs',
    price: 529,
    rating: 4.5,
    reviewCount: 134,
    image: 'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=800&h=600&fit=crop',
    ],
    description: 'Curved barrel chair with upholstered exterior and swivel base. Perfect for conversation areas.',
    features: ['Swivel base', 'Upholstered exterior', 'Curved back', 'Premium foam'],
    styles: ['Modern', 'Transitional'],
    colors: ['gray', 'navy', 'taupe'],
    tags: ['swivel', 'barrel', 'curved', 'versatile'],
    dimensions: {
      width: 30,
      height: 33,
      depth: 32,
      seatHeight: 18
    },
    inStock: true,
    trending: true,
  },
  {
    id: 26,
    name: 'Rattan Peacock Chair',
    category: 'Chairs',
    price: 449,
    rating: 4.6,
    reviewCount: 189,
    image: 'https://images.unsplash.com/photo-1565538810643-b5bdb714032a?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1565538810643-b5bdb714032a?w=800&h=600&fit=crop',
    ],
    description: 'Bohemian rattan peacock chair with woven backrest. Natural finish brings tropical flair to any space.',
    features: ['Hand-woven rattan', 'Natural finish', 'High-back design', 'Comfortable cushion included'],
    styles: ['Bohemian', 'Coastal'],
    colors: ['natural', 'white'],
    tags: ['rattan', 'peacock', 'boho', 'statement'],
    dimensions: {
      width: 36,
      height: 54,
      depth: 32,
      seatHeight: 17
    },
    inStock: true,
  },

  // New Category: Bed Frames
  {
    id: 27,
    name: 'Upholstered Platform Bed',
    category: 'Bed Frames',
    price: 1199,
    rating: 4.8,
    reviewCount: 256,
    image: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800&h=600&fit=crop',
    ],
    description: 'Modern platform bed with upholstered wingback headboard. Available in Queen and King sizes.',
    features: ['Upholstered headboard', 'Solid slat base', 'No box spring needed', 'Available in multiple fabrics'],
    styles: ['Modern', 'Transitional'],
    colors: ['gray', 'navy', 'beige'],
    tags: ['platform', 'upholstered', 'modern', 'queen'],
    dimensions: {
      width: 84,
      height: 52,
      depth: 90
    },
    inStock: true,
    trending: true,
  },
  {
    id: 28,
    name: 'Mid-Century Bed Frame',
    category: 'Bed Frames',
    price: 899,
    rating: 4.7,
    reviewCount: 178,
    image: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800&h=600&fit=crop',
    ],
    description: 'Classic mid-century bed frame with tapered legs and walnut finish. Clean lines and timeless design.',
    features: ['Walnut finish', 'Tapered legs', 'Solid wood construction', 'Center support'],
    styles: ['Mid-Century', 'Scandinavian'],
    colors: ['walnut', 'natural'],
    tags: ['mid-century', 'walnut', 'solid-wood'],
    dimensions: {
      width: 84,
      height: 48,
      depth: 90
    },
    inStock: true,
  },
  {
    id: 29,
    name: 'Iron Canopy Bed',
    category: 'Bed Frames',
    price: 1099,
    rating: 4.6,
    reviewCount: 145,
    image: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800&h=600&fit=crop',
    ],
    description: 'Vintage-inspired iron canopy bed with scrollwork details. Creates a romantic focal point in any bedroom.',
    features: ['Wrought iron frame', 'Scrollwork details', 'Four-post design', 'Matte black finish'],
    styles: ['Industrial', 'Traditional'],
    colors: ['black', 'bronze', 'white'],
    tags: ['canopy', 'iron', 'vintage', 'romantic'],
    dimensions: {
      width: 84,
      height: 72,
      depth: 90
    },
    inStock: true,
  },

  // New Category: Desks
  {
    id: 30,
    name: 'Writing Bureau Desk',
    category: 'Desks',
    price: 649,
    rating: 4.7,
    reviewCount: 234,
    image: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=800&h=600&fit=crop',
    ],
    description: 'Classic writing bureau with multiple drawers and fold-down desktop. Perfect for home office or guest room.',
    features: ['Fold-down desktop', 'Multiple storage drawers', 'Cable management', 'Antique brass hardware'],
    styles: ['Traditional', 'Transitional'],
    colors: ['white', 'espresso', 'gray'],
    tags: ['bureau', 'writing-desk', 'storage', 'compact'],
    dimensions: {
      width: 48,
      height: 42,
      depth: 24
    },
    inStock: true,
  },
  {
    id: 31,
    name: 'Standing Desk Converter',
    category: 'Desks',
    price: 399,
    rating: 4.6,
    reviewCount: 367,
    image: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=800&h=600&fit=crop',
    ],
    description: 'Height-adjustable desk converter that transforms any desk into a standing desk. Electric lift mechanism.',
    features: ['Electric height adjustment', 'Spacious work surface', 'Keyboard tray', 'Memory presets'],
    styles: ['Modern', 'Minimalist'],
    colors: ['black', 'white', 'gray'],
    tags: ['standing-desk', 'adjustable', 'ergonomic', 'converter'],
    dimensions: {
      width: 48,
      minHeight: 6,
      maxHeight: 20,
      depth: 30
    },
    inStock: true,
    trending: true,
  },
  {
    id: 32,
    name: 'Floating Wall Desk',
    category: 'Desks',
    price: 299,
    rating: 4.5,
    reviewCount: 189,
    image: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=800&h=600&fit=crop',
    ],
    description: 'Space-saving floating desk with hidden storage. Perfect for small apartments and home offices.',
    features: ['Wall-mounted design', 'Hidden storage compartment', 'Cable management', 'Fold-down option'],
    styles: ['Modern', 'Minimalist'],
    colors: ['white', 'walnut', 'black'],
    tags: ['wall-mounted', 'space-saving', 'compact', 'modern'],
    dimensions: {
      width: 40,
      height: 20,
      depth: 20
    },
    inStock: true,
  },

  // New Category: Storage
  {
    id: 33,
    name: 'Mid-Century Credenza',
    category: 'Storage',
    price: 799,
    rating: 4.8,
    reviewCount: 145,
    image: 'https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=800&h=600&fit=crop',
    ],
    description: 'Mid-century modern credenza with sliding doors and adjustable shelves. Perfect for dining room or entertainment.',
    features: ['Sliding doors', 'Adjustable shelves', 'Cord management', 'Solid wood legs'],
    styles: ['Mid-Century', 'Scandinavian'],
    colors: ['walnut', 'white', 'teal'],
    tags: ['credenza', 'storage', 'mid-century', 'media-console'],
    dimensions: {
      width: 72,
      height: 34,
      depth: 18
    },
    inStock: true,
    trending: true,
  },
  {
    id: 34,
    name: 'Industrial Bookcase',
    category: 'Storage',
    price: 449,
    rating: 4.6,
    reviewCount: 267,
    image: 'https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=800&h=600&fit=crop',
    ],
    description: '6-shelf industrial bookcase with metal frame and wood shelves. Open design displays books and decor beautifully.',
    features: ['6 adjustable shelves', 'Metal frame', 'Wood shelves', 'Wall anchor included'],
    styles: ['Industrial', 'Rustic'],
    colors: ['black', 'bronze', 'gray'],
    tags: ['bookcase', 'industrial', 'open-shelving', 'metal'],
    dimensions: {
      width: 36,
      height: 72,
      depth: 12
    },
    inStock: true,
  },
  {
    id: 35,
    name: ' rattan Storage Basket Set',
    category: 'Storage',
    price: 89,
    rating: 4.5,
    reviewCount: 423,
    image: 'https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=800&h=600&fit=crop',
    ],
    description: 'Set of 3 handwoven rattan storage baskets with handles. Perfect for organizing any room.',
    features: ['Set of 3', 'Handwoven rattan', 'Built-in handles', 'Nested storage'],
    styles: ['Bohemian', 'Coastal'],
    colors: ['natural', 'white-wash'],
    tags: ['baskets', 'rattan', 'organizing', 'set'],
    dimensions: {
      large: {
        width: 16,
        height: 12,
        depth: 16
      },
      medium: {
        width: 14,
        height: 10,
        depth: 14
      },
      small: {
        width: 12,
        height: 8,
        depth: 12
      }
    },
    inStock: true,
  },

  // New Category: Decor
  {
    id: 36,
    name: 'Floor Mirror',
    category: 'Decor',
    price: 249,
    rating: 4.7,
    reviewCount: 356,
    image: 'https://images.unsplash.com/photo-1618220179428-22790b461013?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1618220179428-22790b461013?w=800&h=600&fit=crop',
    ],
    description: 'Full-length floor mirror with arched top and thin gold frame. Lean or wall-mount design.',
    features: ['Arched top', 'Gold frame', 'Lean or wall-mount', 'HD reflection'],
    styles: ['Modern', 'Glam'],
    colors: ['gold', 'black', 'white'],
    tags: ['mirror', 'full-length', 'arched', 'statement'],
    dimensions: {
      width: 30,
      height: 72,
      depth: 1
    },
    inStock: true,
    trending: true,
  },
  {
    id: 37,
    name: 'Ceramic Vase Set',
    category: 'Decor',
    price: 79,
    rating: 4.6,
    reviewCount: 489,
    image: 'https://images.unsplash.com/photo-1612196808214-b7e239e5f9b7?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1612196808214-b7e239e5f9b7?w=800&h=600&fit=crop',
    ],
    description: 'Set of 3 modern ceramic vases in varying heights. Matte finish with organic shapes.',
    features: ['Set of 3', 'Handcrafted ceramic', 'Matte finish', 'Watertight'],
    styles: ['Modern', 'Minimalist'],
    colors: ['white', 'terracotta', 'black'],
    tags: ['vases', 'ceramic', 'set', 'modern'],
    dimensions: {
      large: {
        height: 14,
        diameter: 5
      },
      medium: {
        height: 10,
        diameter: 4
      },
      small: {
        height: 7,
        diameter: 3
      }
    },
    inStock: true,
  },
  {
    id: 38,
    name: 'Woven Area Rug',
    category: 'Decor',
    price: 299,
    rating: 4.5,
    reviewCount: 234,
    image: 'https://images.unsplash.com/photo-1600166898405-da9535204843?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1600166898405-da9535204843?w=800&h=600&fit=crop',
    ],
    description: 'Handwoven jute area rug with cotton border. Natural texture adds warmth to any space.',
    features: ['Handwoven jute', 'Cotton border', 'Natural material', 'Multiple sizes'],
    styles: ['Bohemian', 'Coastal', 'Rustic'],
    colors: ['natural', 'gray', 'cream'],
    tags: ['rug', 'jute', 'natural', 'handwoven'],
    dimensions: {
      width: 96,
      height: 64
    },
    inStock: true,
  },
  {
    id: 39,
    name: 'Abstract Wall Art',
    category: 'Decor',
    price: 189,
    rating: 4.4,
    reviewCount: 178,
    image: 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=800&h=600&fit=crop',
    ],
    description: 'Modern abstract canvas print with gold leaf accents. Gallery-wrapped canvas ready to hang.',
    features: ['Gallery-wrapped canvas', 'Gold leaf accents', 'Ready to hang', 'Hand-finished details'],
    styles: ['Modern', 'Glam'],
    colors: ['gold', 'black', 'white'],
    tags: ['wall-art', 'abstract', 'canvas', 'gold'],
    dimensions: {
      width: 36,
      height: 48,
      depth: 1
    },
    inStock: true,
  },

  // Additional Products in Existing Categories
  {
    id: 40,
    name: 'Tufted Ottoman',
    category: 'Sofas',
    price: 449,
    rating: 4.6,
    reviewCount: 145,
    image: 'https://images.unsplash.com/photo-1550226891-ef816aed4a98?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1550226891-ef816aed4a98?w=800&h=600&fit=crop',
    ],
    description: 'Versatile tufted ottoman with storage compartment. Can be used as coffee table or extra seating.',
    features: ['Storage compartment', 'Tufted top', 'Solid wood base', 'Versatile use'],
    styles: ['Transitional', 'Modern'],
    colors: ['gray', 'navy', 'cream'],
    tags: ['ottoman', 'storage', 'versatile', 'tufted'],
    dimensions: {
      width: 48,
      height: 18,
      depth: 30
    },
    inStock: true,
  },
  {
    id: 41,
    name: ' Adjustable Bar Stool',
    category: 'Chairs',
    price: 179,
    rating: 4.5,
    reviewCount: 267,
    image: 'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=800&h=600&fit=crop',
    ],
    description: 'Modern adjustable bar stool with backrest and swivel seat. Chrome base with upholstered cushion.',
    features: ['Adjustable height', 'Swivel seat', 'Backrest included', 'Chrome base'],
    styles: ['Modern', 'Industrial'],
    colors: ['black', 'gray', 'white'],
    tags: ['bar-stool', 'adjustable', 'swivel', 'kitchen'],
    dimensions: {
      width: 18,
      minHeight: 24,
      maxHeight: 32,
      depth: 18,
      seatHeight: 24
    },
    inStock: true,
  },
  {
    id: 42,
    name: 'Pendant Light Cluster',
    category: 'Lamps',
    price: 349,
    rating: 4.7,
    reviewCount: 189,
    image: 'https://images.unsplash.com/photo-1540932296774-3bedde00830c?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1540932296774-3bedde00830c?w=800&h=600&fit=crop',
    ],
    description: 'Cluster of 3 globe pendant lights at varying heights. Creates a stunning focal point over dining tables.',
    features: ['Set of 3 pendants', 'Glass globes', 'Adjustable cords', 'Hardwired installation'],
    styles: ['Modern', 'Minimalist'],
    colors: ['brass', 'chrome', 'black'],
    tags: ['pendant', 'cluster', 'glass', 'modern'],
    dimensions: {
      height: 18,
      diameter: 10
    },
    inStock: true,
    trending: true,
  },
  {
    id: 43,
    name: 'Folding Card Table',
    category: 'Tables',
    price: 199,
    rating: 4.4,
    reviewCount: 123,
    image: 'https://images.unsplash.com/photo-1617104678098-ab8fc7a4e682?w=600&h=400&fit=crop',
    images: [
      'https://images.unsplash.com/photo-1617104678098-ab8fc7a4e682?w=800&h=600&fit=crop',
    ],
    description: 'Versatile folding table perfect for game nights or extra dining space. Square design seats 4.',
    features: ['Folding design', 'Seats 4', 'Easy storage', 'Locking mechanism'],
    styles: ['Traditional', 'Transitional'],
    colors: ['white', 'black', 'natural'],
    tags: ['folding', 'game-table', 'versatile', 'compact'],
    dimensions: {
      width: 36,
      height: 29,
      depth: 36
    },
    inStock: true,
  },
];

export const CATEGORIES = [
  { id: 'all', name: 'All Products', icon: '🛋️' },
  { id: 'sofas', name: 'Sofas', icon: '🛋️' },
  { id: 'tables', name: 'Tables', icon: '🪵' },
  { id: 'lamps', name: 'Lamps', icon: '💡' },
  { id: 'chairs', name: 'Chairs', icon: '🪑' },
  { id: 'bed-frames', name: 'Bed Frames', icon: '🛏️' },
  { id: 'desks', name: 'Desks', icon: '🖥️' },
  { id: 'storage', name: 'Storage', icon: '🗄️' },
  { id: 'decor', name: 'Decor', icon: '🖼️' },
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

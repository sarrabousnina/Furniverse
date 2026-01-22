// AI-powered recommendations engine (simulated)

// Calculate how well a product matches a room's style preferences
export const calculateStyleMatch = (product, room) => {
  if (!room || !room.styles || room.styles.length === 0) return null;

  let matchScore = 0;
  let matchReasons = [];

  // Check style matches
  const productStyles = product.styles || [];
  const matchingStyles = room.styles.filter(style =>
    productStyles.some(ps => ps.toLowerCase() === style.toLowerCase())
  );

  if (matchingStyles.length > 0) {
    matchScore += 40;
    matchReasons.push(`Matches your ${matchingStyles[0]} style`);
  }

  // Check budget match
  if (room.budgetMin && room.budgetMax) {
    if (product.price >= room.budgetMin && product.price <= room.budgetMax) {
      matchScore += 30;
      matchReasons.push('Within your budget');
    } else if (product.price < room.budgetMin) {
      matchScore += 15;
      matchReasons.push('Below your min budget (great deal!)');
    } else if (product.price > room.budgetMax) {
      matchScore -= 20;
      matchReasons.push('Above your max budget');
    }
  }

  // Check color preferences based on existing furniture
  if (room.existingFurniture) {
    const furniture = room.existingFurniture.toLowerCase();
    const colors = ['navy', 'gray', 'beige', 'brown', 'white', 'black', 'emerald', 'green', 'walnut'];

    colors.forEach(color => {
      if (furniture.includes(color) && product.colors && product.colors.includes(color)) {
        matchScore += 10;
        matchReasons.push(`Complements your ${color} pieces`);
      }
    });

    // Check texture/material matches
    if (furniture.includes('velvet') && product.tags && product.tags.includes('velvet')) {
      matchScore += 15;
      matchReasons.push('Velvet texture like your existing pieces');
    }
    if (furniture.includes('walnut') && product.tags && product.tags.includes('walnut')) {
      matchScore += 15;
      matchReasons.push('Walnut finish to match your furniture');
    }
  }

  // Normalize score to 0-100
  matchScore = Math.max(0, Math.min(100, matchScore));

  return {
    score: Math.round(matchScore),
    reasons: matchReasons,
  };
};

// Get recommended products for a room
export const getRecommendedProducts = (room, products, limit = 8) => {
  if (!room) return [];

  const productsWithScores = products.map(product => {
    const matchData = calculateStyleMatch(product, room);
    return {
      ...product,
      matchScore: matchData ? matchData.score : null,
      matchReasons: matchData ? matchData.reasons : [],
    };
  });

  // Sort by match score (descending) and filter out null scores
  const recommended = productsWithScores
    .filter(p => p.matchScore !== null && p.matchScore > 30)
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, limit);

  return recommended;
};

// Get trending products
export const getTrendingProducts = (products, limit = 8) => {
  return products
    .filter(p => p.trending)
    .slice(0, limit);
};

// Get products by category
export const getProductsByCategory = (products, category) => {
  if (category === 'all') return products;
  return products.filter(p =>
    p.category.toLowerCase() === category.toLowerCase()
  );
};

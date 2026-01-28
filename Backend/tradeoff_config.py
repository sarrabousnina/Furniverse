"""
Configuration and data structures for trade-off recommendation system
Data-driven instead of hardcoded if-else logic
"""

# ============================================================================
# ATTRIBUTE HIERARCHIES (with synonyms and relationships)
# ============================================================================

MATERIAL_HIERARCHY = {
    "leather": {
        "variants": ["genuine leather", "real leather", "full grain"],
        "alternatives": ["pu leather", "faux leather", "bonded leather", "vegan leather"],
        "related": ["leatherette", "synthetic leather"],
        "benefits": ["durable", "luxurious", "premium"],
        "tradeoffs": {
            "pu leather": {
                "loses": ["not genuine leather", "synthetic material"],
                "gains": ["more affordable", "easier to clean", "cruelty-free"]
            },
            "fabric": {
                "loses": ["not leather"],
                "gains": ["softer texture", "breathable", "lighter weight"]
            },
            "velvet": {
                "loses": ["not leather"],
                "gains": ["plush feel", "luxurious appearance", "softer"]
            }
        }
    },
    "velvet": {
        "variants": ["crushed velvet", "plush velvet"],
        "alternatives": ["fabric", "corduroy", "chenille"],
        "benefits": ["luxurious", "soft", "plush"],
        "tradeoffs": {
            "fabric": {
                "loses": ["not velvet texture"],
                "gains": ["more durable", "easier to clean"]
            }
        }
    },
    "fabric": {
        "variants": ["cotton", "linen", "polyester", "blend"],
        "alternatives": ["velvet", "leather", "microfiber"],
        "benefits": ["breathable", "versatile", "comfortable"]
    },
    "wood": {
        "variants": ["solid wood", "hardwood", "softwood", "oak", "walnut", "pine"],
        "alternatives": ["metal", "glass", "particle board", "mdf"],
        "benefits": ["natural", "durable", "classic"],
        "tradeoffs": {
            "metal": {
                "loses": ["not wood", "industrial look"],
                "gains": ["more durable", "modern appearance", "lighter"]
            }
        }
    },
    "metal": {
        "variants": ["steel", "iron", "aluminum", "brass", "chrome"],
        "alternatives": ["wood", "glass", "plastic"],
        "benefits": ["durable", "modern", "strong"]
    }
}

STYLE_HIERARCHY = {
    "modern": {
        "variants": ["contemporary", "mid-century modern", "minimalist"],
        "alternatives": ["traditional", "industrial", "scandinavian"],
        "keywords": ["sleek", "clean lines", "minimal", "streamlined"],
        "opposites": ["traditional", "vintage", "rustic", "ornate"],
        "tradeoffs": {
            "traditional": {
                "loses": ["not modern style", "classic design"],
                "gains": ["timeless appeal", "more decorative details"]
            },
            "industrial": {
                "loses": ["not sleek modern"],
                "gains": ["urban aesthetic", "raw materials", "bold look"]
            }
        }
    },
    "contemporary": {
        "variants": ["modern contemporary"],
        "alternatives": ["modern", "transitional"],
        "keywords": ["current", "today's trends", "up-to-date"]
    },
    "traditional": {
        "variants": ["classic", "vintage", "antique-style"],
        "alternatives": ["modern", "contemporary", "transitional"],
        "keywords": ["ornate", "elegant", "timeless", "classic"],
        "opposites": ["modern", "minimalist", "sleek"]
    },
    "industrial": {
        "variants": ["urban", "loft-style"],
        "alternatives": ["modern", "rustic industrial"],
        "keywords": ["metal", "raw", "exposed", "utilitarian"]
    },
    "minimalist": {
        "variants": ["simple", "clean"],
        "alternatives": ["modern", "scandinavian"],
        "keywords": ["minimal", " streamlined", "uncluttered"]
    },
    "scandinavian": {
        "variants": ["nordic", "danish modern"],
        "alternatives": ["minimalist", "modern"],
        "keywords": ["light wood", "cozy", "functional"]
    }
}

COLOR_HIERARCHY = {
    "red": {
        "variants": ["crimson", "burgundy", "maroon", "cherry", "ruby"],
        "related": ["pink", "orange", "rust"],
        "opposites": ["green", "blue"]
    },
    "blue": {
        "variants": ["navy", "azure", "teal", "cobalt", "royal blue"],
        "related": ["cyan", "turquoise", "indigo"],
        "opposites": ["orange", "red"]
    },
    "green": {
        "variants": ["olive", "emerald", "sage", "forest", "mint"],
        "related": ["teal", "turquoise", "lime"],
        "opposites": ["red", "pink"]
    },
    "neutral": {
        "variants": ["gray", "grey", "beige", "cream", "white", "black", "taupe"],
        "benefits": ["versatile", "matches everything", "timeless"]
    }
}

COMFORT_HIERARCHY = {
    "high": {
        "keywords": ["comfy", "comfortable", "plush", "soft", "cushioned", "cozy"],
        "indicators": ["thick cushion", "memory foam", "padded", "upholstered"]
    },
    "medium": {
        "keywords": ["firm", "supportive"]
    }
}

# ============================================================================
# BUDGET THRESHOLDS (market-aware pricing)
# ============================================================================

BUDGET_THRESHOLDS = {
    "sofa": {
        "low": 300,
        "medium": 800,
        "high": 1500,
        "premium": 2500
    },
    "chair": {
        "low": 100,
        "medium": 300,
        "high": 600,
        "premium": 1000
    },
    "table": {
        "low": 150,
        "medium": 500,
        "high": 1000,
        "premium": 2000
    },
    "bed": {
        "low": 300,
        "medium": 800,
        "high": 1500,
        "premium": 3000
    }
}

# ============================================================================
# EXPLANATION TEMPLATES
# ============================================================================

EXPLANATION_TEMPLATES = {
    "budget": {
        "under": "✓ Under budget by ${savings:.0f} (${price:.0f} vs {budget:.0f})",
        "exact": "✓ Exactly your budget of ${budget:.0f}",
        "over": "✗ Over budget by ${overage:.0f} (${price:.0f} vs {budget:.0f})"
    },
    "material": {
        "exact": "✓ {material} material",
        "variant": "✓ {variant} (premium {material})",
        "alternative": "✓ {alt} (alternative to {material})",
        "missing": "✗ Not {material}",
        "benefit": "✓ {benefit} (compared to {material})"
    },
    "style": {
        "exact": "✓ {style} style",
        "related": "✓ {related} (similar to {style})",
        "opposite": "✗ {actual} (not {requested})"
    },
    "color": {
        "exact": "✓ {color} color as requested",
        "variant": "✓ {variant} shade of {color}",
        "different": "✗ {actual} instead of {requested}"
    },
    "comfort": {
        "high": "✓ Comfortable cushioning",
        "medium": "✓ Standard comfort level",
        "low": "✗ May not be as comfortable"
    }
}

# ============================================================================
# ATTRIBUTE EXTRACTION RULES
# ============================================================================

EXTRACTION_RULES = {
    "budget": {
        "patterns": [
            r'under\s+\$?(\d+)',
            r'budget\s+(?:of\s+)?\$?(\d+)',
            r'cheap(?:est)?\s+(?:under\s+)?\$?(\d+)',
            r'(?:max|maximum)\s+(?:?:price|cost)\s+(?:of\s+)?\$?(\d+)',
            r'less\s+than\s+\$?(\d+)',
            r'below\s+\$?(\d+)'
        ],
        "extract": lambda match: float(match.group(1))
    },
    "material": {
        "hierarchy": MATERIAL_HIERARCHY,
        "match_type": "hierarchy"  # Use hierarchy-based matching
    },
    "style": {
        "hierarchy": STYLE_HIERARCHY,
        "match_type": "hierarchy"
    },
    "color": {
        "hierarchy": COLOR_HIERARCHY,
        "match_type": "hierarchy"
    },
    "comfort": {
        "keywords": COMFORT_HIERARCHY["high"]["keywords"],
        "match_type": "keyword"
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_material_variant(material: str, product_text: str) -> dict:
    """
    Determine what type of material a product has relative to requested material

    Returns:
        dict with: match_type, variant_name, tradeoffs
    """
    from ..utils.text_similarity import fuzzy_match

    material_lower = material.lower()
    product_text_lower = product_text.lower()

    # Check for exact match or variant
    if material_lower in product_text_lower:
        return {
            "match_type": "exact",
            "variant_name": material,
            "tradeoffs": None
        }

    # Check hierarchy for variants
    if material in MATERIAL_HIERARCHY:
        material_info = MATERIAL_HIERARCHY[material]

        # Check for variants
        for variant in material_info.get("variants", []):
            if variant in product_text_lower:
                return {
                    "match_type": "variant",
                    "variant_name": variant,
                    "tradeoffs": None
                }

        # Check for alternatives
        for alt in material_info.get("alternatives", []):
            if alt in product_text_lower:
                tradeoffs = material_info.get("tradeoffs", {}).get(alt, {})
                return {
                    "match_type": "alternative",
                    "variant_name": alt,
                    "tradeoffs": tradeoffs
                }

    return {
        "match_type": "none",
        "variant_name": None,
        "tradeoffs": None
    }


def find_style_variant(style: str, product_text: str) -> dict:
    """Determine what style a product has relative to requested style"""

    style_lower = style.lower()
    product_text_lower = product_text.lower()

    # Check for exact match
    if style_lower in product_text_lower:
        return {
            "match_type": "exact",
            "style_name": style,
            "is_opposite": False
        }

    # Check hierarchy
    if style in STYLE_HIERARCHY:
        style_info = STYLE_HIERARCHY[style]

        # Check for related styles
        for variant in style_info.get("variants", []):
            if variant in product_text_lower:
                return {
                    "match_type": "related",
                    "style_name": variant,
                    "is_opposite": False
                }

        # Check for opposites
        for opposite in style_info.get("opposites", []):
            if opposite in product_text_lower:
                return {
                    "match_type": "opposite",
                    "style_name": opposite,
                    "is_opposite": True
                }

    return {
        "match_type": "none",
        "style_name": None,
        "is_opposite": False
    }


def is_market_prealistic(material: str, budget: float, category: str = None) -> dict:
    """
    Check if a request is market-realistic

    Returns:
        dict with: is_realistic, suggested_alternative, explanation
    """
    # Rough price estimates for materials
    material_prices = {
        "leather": {"min": 1000, "typical": 1500},
        "genuine leather": {"min": 1200, "typical": 1800},
        "velvet": {"min": 400, "typical": 700},
        "fabric": {"min": 200, "typical": 500},
        "wood": {"min": 300, "typical": 600}
    }

    if material in material_prices:
        price_info = material_prices[material]
        if budget < price_info["min"]:
            return {
                "is_realistic": False,
                "suggested_alternative": "fabric" if material == "leather" else None,
                "explanation": f"{material.capitalize()} typically starts at ${price_info['min']}, but your budget is ${budget}"
            }

    return {
        "is_realistic": True,
        "suggested_alternative": None,
        "explanation": None
    }

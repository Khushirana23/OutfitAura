"""OutfitAura luxury fashion initial dataset."""
from datetime import datetime
from typing import List, Dict, Any

SEED_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": "prod_silk_slip_01",
        "name": "Silk Slip Dress",
        "slug": "silk-slip-dress",
        "category": "Women",
        "subcategory": "Dresses",
        "price": 185.00,
        "original_price": 220.00,
        "description": "Crafted from 100% 19-momme pure mulberry silk, this bias-cut slip dress drapes effortlessly along the body. Featuring delicate adjustable straps, a gentle scoop neckline, and a subtle side slit for movement.",
        "details": [
            "100% Premium Mulberry Silk (19 Momme)",
            "Bias-cut silhouette for natural drape and contouring",
            "Adjustable micro-bias spaghetti straps",
            "Mid-calf length with 8-inch side slit",
            "Dry clean or delicate hand wash cold"
        ],
        "images": [
            "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1000&q=80"
        ],
        "thumbnail": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=600&q=80",
        "colors": [
            {"name": "Blush Pink", "hex": "#fadadd", "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=1000&q=80"},
            {"name": "Noir Black", "hex": "#1b1c1c", "image": "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1000&q=80"},
            {"name": "Ivory Pearl", "hex": "#f5f3f3", "image": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1000&q=80"}
        ],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "stock": 42,
        "rating": 4.9,
        "review_count": 84,
        "is_featured": True,
        "is_new_arrival": True,
        "is_trending": True,
        "is_sale": False,
        "tags": ["silk", "slip dress", "minimalist", "luxury", "evening"]
    },
    {
        "id": "prod_linen_blazer_02",
        "name": "Tailored Relaxed Blazer",
        "slug": "tailored-relaxed-blazer",
        "category": "Women",
        "subcategory": "Outerwear",
        "price": 240.00,
        "original_price": 290.00,
        "description": "An architectural oversized blazer constructed in crisp Italian linen blend. Structured shoulder pads meet a fluid unlined body, creating the ultimate power silhouette.",
        "details": [
            "Italian Linen & Tencel blend",
            "Double-breasted horn button closure",
            "Interior welt pocket and functional flap pockets",
            "Light shoulder padding for architectural form"
        ],
        "images": [
            "https://images.unsplash.com/photo-1584273143981-41c073dfe8f8?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=1000&q=80"
        ],
        "thumbnail": "https://images.unsplash.com/photo-1584273143981-41c073dfe8f8?auto=format&fit=crop&w=600&q=80",
        "colors": [
            {"name": "Sand Dune", "hex": "#e9e8e7"},
            {"name": "Espresso", "hex": "#303031"}
        ],
        "sizes": ["XS", "S", "M", "L"],
        "stock": 28,
        "rating": 4.8,
        "review_count": 46,
        "is_featured": True,
        "is_new_arrival": True,
        "is_trending": False,
        "is_sale": False,
        "tags": ["blazer", "tailored", "linen", "oversized"]
    },
    {
        "id": "prod_pleated_trouser_03",
        "name": "Pleated Wide-Leg Trouser",
        "slug": "pleated-wide-leg-trouser",
        "category": "Women",
        "subcategory": "Trousers",
        "price": 145.00,
        "original_price": 175.00,
        "description": "High-waisted trousers with dramatic double front pleats. Flowing straight leg cut engineered for an elongated, statuesque proportion.",
        "details": [
            "Flowy wool-crepe blend",
            "High rise with deep front pleats",
            "Concealed zip fly and tab closure",
            "Side slant pockets"
        ],
        "images": [
            "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1000&q=80"
        ],
        "thumbnail": "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=600&q=80",
        "colors": [
            {"name": "Charcoal Grey", "hex": "#4f4445"},
            {"name": "Chalk White", "hex": "#ffffff"}
        ],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "stock": 35,
        "rating": 4.9,
        "review_count": 62,
        "is_featured": True,
        "is_new_arrival": False,
        "is_trending": True,
        "is_sale": False,
        "tags": ["trousers", "pleated", "wide-leg", "high-rise"]
    },
    {
        "id": "prod_cashmere_overcoat_04",
        "name": "Cashmere Wrap Overcoat",
        "slug": "cashmere-wrap-overcoat",
        "category": "Men",
        "subcategory": "Outerwear",
        "price": 420.00,
        "original_price": 495.00,
        "description": "Sumptuous double-faced Mongolian cashmere tailored into a relaxed silhouette with a detachable belt and notched lapels.",
        "details": [
            "100% Sustainable Mongolian Cashmere",
            "Double-faced hand-finished construction",
            "Self-tie sash belt with belt loops",
            "Deep patch pockets"
        ],
        "images": [
            "https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1000&q=80"
        ],
        "thumbnail": "https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=600&q=80",
        "colors": [
            {"name": "Camel Luxe", "hex": "#c6a682"},
            {"name": "Midnight Obsidian", "hex": "#1a1c1c"}
        ],
        "sizes": ["S", "M", "L", "XL"],
        "stock": 18,
        "rating": 5.0,
        "review_count": 29,
        "is_featured": True,
        "is_new_arrival": True,
        "is_trending": True,
        "is_sale": False,
        "tags": ["cashmere", "coat", "men", "winter", "luxury"]
    },
    {
        "id": "prod_cotton_poplin_shirt_05",
        "name": "Sculptural Poplin Shirt",
        "slug": "sculptural-poplin-shirt",
        "category": "Men",
        "subcategory": "Shirts",
        "price": 120.00,
        "original_price": 140.00,
        "description": "Crisp organic cotton poplin button-down with dropped shoulders and architectural French cuffs.",
        "details": [
            "100% GOTS Certified Organic Cotton",
            "Mother-of-pearl buttons",
            "Subtle back pleat for freedom of movement"
        ],
        "images": [
            "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=1000&q=80"
        ],
        "thumbnail": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=600&q=80",
        "colors": [
            {"name": "Optical White", "hex": "#ffffff"},
            {"name": "Pale Celeste", "hex": "#dbeafe"}
        ],
        "sizes": ["S", "M", "L", "XL"],
        "stock": 50,
        "rating": 4.7,
        "review_count": 31,
        "is_featured": False,
        "is_new_arrival": True,
        "is_trending": False,
        "is_sale": False,
        "tags": ["shirt", "cotton", "organic", "minimal"]
    },
    {
        "id": "prod_ribbed_knit_top_06",
        "name": "Fine-Ribbed Silk Tank",
        "slug": "fine-ribbed-silk-tank",
        "category": "Women",
        "subcategory": "Tops",
        "price": 85.00,
        "original_price": 110.00,
        "description": "A second-skin micro-ribbed knit tank top crafted from a silk-cotton yarn blend. High racer neckline and seamless edging.",
        "details": [
            "70% Mulberry Silk, 30% Long-Staple Cotton",
            "High halter-racer neckline",
            "Form-fitting with generous stretch"
        ],
        "images": [
            "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=1000&q=80"
        ],
        "thumbnail": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=600&q=80",
        "colors": [
            {"name": "Rose Quartz", "hex": "#fbdbde"},
            {"name": "Onyx", "hex": "#1b1c1c"}
        ],
        "sizes": ["XS", "S", "M", "L"],
        "stock": 60,
        "rating": 4.9,
        "review_count": 95,
        "is_featured": False,
        "is_new_arrival": False,
        "is_trending": True,
        "is_sale": True,
        "tags": ["tank", "silk", "ribbed", "basics", "sale"]
    }
]

SEED_REVIEWS: List[Dict[str, Any]] = [
    {
        "id": "rev_01",
        "product_id": "prod_silk_slip_01",
        "user_id": "user_demo_01",
        "user_name": "Aura Muse",
        "rating": 5,
        "title": "The most flattering slip dress I own",
        "comment": "The blush pink color is breathtaking in person. The silk feels feather-light yet opaque enough to wear out with zero hesitation.",
        "size_purchased": "S",
        "color_purchased": "Blush Pink",
        "created_at": datetime.now()
    }
]

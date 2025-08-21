#!/usr/bin/env python3
"""
Seed script to populate the database with sample data
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8008/api/v1"
AUTH_TOKEN = sys.argv[1] if len(sys.argv) > 1 else "your_token_here"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Sample Categories
categories = [
    {"name": "Electronics", "slug": "electronics", "description": "Smartphones, Laptops, and Gadgets"},
    {"name": "Fashion", "slug": "fashion", "description": "Clothing, Shoes, and Accessories"},
    {"name": "Home & Garden", "slug": "home-garden", "description": "Furniture, Decor, and Garden Tools"},
    {"name": "Sports", "slug": "sports", "description": "Sports Equipment and Outdoor Gear"},
    {"name": "Books", "slug": "books", "description": "Books, E-books, and Audiobooks"},
]

# Sample Products
products = [
    {
        "name": "iPhone 15 Pro Max",
        "slug": "iphone-15-pro-max",
        "description": "Latest Apple smartphone with titanium design and advanced camera system",
        "price": 1199.99,
        "stock_quantity": 50,
        "tags": ["smartphone", "apple", "5g", "camera"],
        "specifications": {
            "screen": "6.7-inch Super Retina XDR",
            "chip": "A17 Pro",
            "camera": "48MP main",
            "battery": "All-day battery life"
        }
    },
    {
        "name": "MacBook Pro 16-inch",
        "slug": "macbook-pro-16",
        "description": "Powerful laptop for professionals with M3 Max chip",
        "price": 2499.99,
        "stock_quantity": 30,
        "tags": ["laptop", "apple", "professional", "m3"],
        "specifications": {
            "processor": "Apple M3 Max",
            "ram": "36GB",
            "storage": "1TB SSD",
            "display": "16-inch Liquid Retina XDR"
        }
    },
    {
        "name": "Nike Air Max 2024",
        "slug": "nike-air-max-2024",
        "description": "Premium running shoes with maximum comfort and style",
        "price": 189.99,
        "stock_quantity": 100,
        "tags": ["shoes", "running", "nike", "sports"],
        "specifications": {
            "material": "Flyknit upper",
            "sole": "Air Max cushioning",
            "weight": "295g",
            "type": "Running"
        }
    },
    {
        "name": "Samsung 65\" OLED Smart TV",
        "slug": "samsung-65-oled-tv",
        "description": "4K OLED TV with stunning picture quality and smart features",
        "price": 1799.99,
        "stock_quantity": 20,
        "tags": ["tv", "4k", "oled", "smart"],
        "specifications": {
            "resolution": "4K UHD",
            "size": "65 inches",
            "hdr": "HDR10+",
            "smart": "Tizen OS"
        }
    },
    {
        "name": "Sony WH-1000XM5 Headphones",
        "slug": "sony-wh1000xm5",
        "description": "Industry-leading noise canceling wireless headphones",
        "price": 399.99,
        "stock_quantity": 75,
        "tags": ["headphones", "wireless", "noise-canceling", "sony"],
        "specifications": {
            "battery": "30 hours",
            "noise_canceling": "Industry-leading",
            "drivers": "30mm",
            "bluetooth": "5.2"
        }
    },
    {
        "name": "Dyson V15 Detect",
        "slug": "dyson-v15-detect",
        "description": "Advanced cordless vacuum with laser dust detection",
        "price": 749.99,
        "stock_quantity": 40,
        "tags": ["vacuum", "cordless", "dyson", "home"],
        "specifications": {
            "runtime": "60 minutes",
            "suction": "230AW",
            "bin": "0.77L",
            "filtration": "HEPA"
        }
    },
    {
        "name": "Canon EOS R5",
        "slug": "canon-eos-r5",
        "description": "Professional mirrorless camera with 45MP sensor",
        "price": 3899.99,
        "stock_quantity": 15,
        "tags": ["camera", "mirrorless", "professional", "canon"],
        "specifications": {
            "sensor": "45MP Full-frame",
            "video": "8K RAW",
            "autofocus": "Dual Pixel CMOS AF II",
            "stabilization": "8-stop IBIS"
        }
    },
    {
        "name": "Lululemon Yoga Mat",
        "slug": "lululemon-yoga-mat",
        "description": "Premium yoga mat with superior grip and cushioning",
        "price": 128.00,
        "stock_quantity": 200,
        "tags": ["yoga", "fitness", "mat", "lululemon"],
        "specifications": {
            "thickness": "5mm",
            "material": "Natural rubber",
            "length": "71 inches",
            "weight": "5.24 lbs"
        }
    },
    {
        "name": "Patagonia Down Jacket",
        "slug": "patagonia-down-jacket",
        "description": "Sustainable down jacket for extreme cold weather",
        "price": 349.00,
        "stock_quantity": 60,
        "tags": ["jacket", "outdoor", "sustainable", "patagonia"],
        "specifications": {
            "insulation": "800-fill recycled down",
            "shell": "100% recycled polyester",
            "weight": "371g",
            "pockets": "3 zippered"
        }
    },
    {
        "name": "Kindle Oasis",
        "slug": "kindle-oasis",
        "description": "Premium e-reader with adjustable warm light",
        "price": 249.99,
        "stock_quantity": 80,
        "tags": ["ereader", "kindle", "books", "amazon"],
        "specifications": {
            "screen": "7-inch 300ppi",
            "storage": "32GB",
            "battery": "Weeks of reading",
            "waterproof": "IPX8"
        }
    }
]

def create_categories():
    """Create sample categories"""
    created_categories = []
    for category in categories:
        response = requests.post(
            f"{BASE_URL}/categories",
            headers=headers,
            json=category
        )
        if response.status_code == 201:
            cat_data = response.json()
            created_categories.append(cat_data)
            print(f"✓ Created category: {cat_data['name']}")
        else:
            print(f"✗ Failed to create category: {category['name']}")
            print(f"  Error: {response.text}")
    return created_categories

def create_products(category_map):
    """Create sample products"""
    # Map products to categories
    for i, product in enumerate(products):
        # Determine category
        if i < 2:  # First 2 products -> Electronics
            cat_id = category_map.get("Electronics")
        elif i == 2:  # Nike shoes -> Fashion
            cat_id = category_map.get("Fashion")
        elif i in [3, 5]:  # TV and Vacuum -> Home & Garden
            cat_id = category_map.get("Home & Garden")
        elif i in [7, 8]:  # Yoga mat and Jacket -> Sports
            cat_id = category_map.get("Sports")
        elif i == 9:  # Kindle -> Books
            cat_id = category_map.get("Books")
        else:  # Others -> Electronics
            cat_id = category_map.get("Electronics")
        
        # Only add category_id if it exists
        if cat_id:
            product["category_id"] = cat_id
    
    for product in products:
        response = requests.post(
            f"{BASE_URL}/products",
            headers=headers,
            json=product
        )
        if response.status_code == 201:
            prod_data = response.json()
            print(f"✓ Created product: {prod_data['name']} - ${prod_data['price']}")
        else:
            print(f"✗ Failed to create product: {product['name']}")
            print(f"  Error: {response.text}")

def main():
    print("🌱 Starting database seeding...")
    print(f"📍 Using API: {BASE_URL}")
    print("-" * 50)
    
    # Create categories
    print("\n📁 Creating categories...")
    created_cats = create_categories()
    
    # Create a map of category names to IDs
    category_map = {cat['name']: cat['id'] for cat in created_cats}
    
    # Create products
    print("\n📦 Creating products...")
    create_products(category_map)
    
    print("\n✨ Seeding complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_data.py <auth_token>")
        print("Please provide your authentication token as an argument")
        sys.exit(1)
    main()
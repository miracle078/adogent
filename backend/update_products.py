#!/usr/bin/env python3
"""
Script to update all products to be active and featured
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

# Get all products
response = requests.get(f"{BASE_URL}/products", headers=headers)
products_data = response.json()

if "products" in products_data:
    products = products_data["products"]
else:
    products = products_data

print(f"Found {len(products)} products to update")

# Update each product
for product in products:
    product_id = product["id"]
    
    # Update product to be active and featured
    update_data = {
        "status": "ACTIVE",
        "is_featured": True,
        "quantity": 50,  # Set stock quantity
        "stock_quantity": 50,  # Try both field names
        "is_visible": True
    }
    
    response = requests.put(
        f"{BASE_URL}/products/{product_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        print(f"✓ Updated product: {product['name']}")
    else:
        print(f"✗ Failed to update product: {product['name']}")
        print(f"  Error: {response.text}")

print("\n✨ Update complete!")
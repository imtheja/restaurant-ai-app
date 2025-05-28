#!/usr/bin/env python3
"""
Add a new restaurant to the system

Usage:
    python add_restaurant.py --name "Restaurant Name" --subdomain "subdomain" --slug "url-slug"
"""

import asyncio
import asyncpg
import argparse
import os
import json
from datetime import datetime
import sys

async def add_restaurant(args):
    """Add a new restaurant to the database"""
    
    # Connect to database
    db_url = os.getenv('DATABASE_URL', 'postgresql://restaurant_user:restaurant_pass@localhost:5432/restaurant_ai')
    conn = await asyncpg.connect(db_url)
    
    try:
        # Check if subdomain/slug already exists
        existing = await conn.fetchrow(
            "SELECT id FROM restaurants WHERE subdomain = $1 OR slug = $2",
            args.subdomain, args.slug
        )
        
        if existing:
            print(f"❌ Error: Subdomain '{args.subdomain}' or slug '{args.slug}' already exists!")
            return False
        
        # Prepare theme config
        theme_config = {
            'primary_color': args.primary_color,
            'logo_position': 'left',
            'chat_position': 'right'
        }
        
        # Insert restaurant
        restaurant_id = await conn.fetchval(
            """
            INSERT INTO restaurants 
            (name, subdomain, slug, description, theme_config, ai_personality, ai_name, welcome_message)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            args.name,
            args.subdomain,
            args.slug,
            args.description or f"Welcome to {args.name}",
            json.dumps(theme_config),
            args.ai_personality or "warm, friendly, and knowledgeable about our menu",
            args.ai_name or "Sophie",
            args.welcome_message or f"Hi! I'm {args.ai_name or 'Sophie'} from {args.name}. What can I help you find today?"
        )
        
        print(f"✅ Restaurant '{args.name}' created successfully!")
        print(f"   ID: {restaurant_id}")
        print(f"   URL: https://{args.subdomain}.{os.getenv('APP_DOMAIN', 'restaurant-ai.com')}")
        print(f"   Alt URL: https://{os.getenv('APP_DOMAIN', 'restaurant-ai.com')}/r/{args.slug}")
        
        # Add sample menu items if requested
        if args.add_samples:
            await add_sample_menu(conn, restaurant_id, args.name)
        
        return True
        
    finally:
        await conn.close()

async def add_sample_menu(conn, restaurant_id, restaurant_name):
    """Add sample menu items"""
    print("\n📝 Adding sample menu items...")
    
    sample_items = [
        {
            'name': 'Signature Appetizer',
            'description': f'Our famous starter that captures the essence of {restaurant_name}',
            'price': 12.99,
            'category': 'appetizer',
            'vegetarian': True,
            'prep_time': '10 minutes'
        },
        {
            'name': 'Chef\'s Special',
            'description': 'Daily creation by our head chef using the freshest ingredients',
            'price': 28.99,
            'category': 'main',
            'vegetarian': False,
            'prep_time': '25 minutes'
        },
        {
            'name': 'House Salad',
            'description': 'Fresh greens with our signature dressing',
            'price': 9.99,
            'category': 'appetizer',
            'vegetarian': True,
            'vegan': True,
            'gluten_free': True,
            'prep_time': '5 minutes'
        },
        {
            'name': 'Decadent Dessert',
            'description': 'Our award-winning dessert that you can\'t miss',
            'price': 8.99,
            'category': 'dessert',
            'vegetarian': True,
            'prep_time': '10 minutes'
        }
    ]
    
    for idx, item in enumerate(sample_items):
        await conn.execute(
            """
            INSERT INTO menu_items 
            (restaurant_id, name, description, price, category, vegetarian, vegan, 
             gluten_free, prep_time, display_order)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            restaurant_id,
            item['name'],
            item['description'],
            item['price'],
            item['category'],
            item.get('vegetarian', False),
            item.get('vegan', False),
            item.get('gluten_free', False),
            item.get('prep_time', '15 minutes'),
            idx
        )
    
    print(f"✅ Added {len(sample_items)} sample menu items")

async def list_restaurants():
    """List all restaurants"""
    db_url = os.getenv('DATABASE_URL', 'postgresql://restaurant_user:restaurant_pass@localhost:5432/restaurant_ai')
    conn = await asyncpg.connect(db_url)
    
    try:
        restaurants = await conn.fetch(
            """
            SELECT id, name, subdomain, slug, active, created_at
            FROM restaurants
            ORDER BY created_at DESC
            """
        )
        
        print("\n🍽️  Restaurants in the system:")
        print("-" * 80)
        
        for r in restaurants:
            status = "✅ Active" if r['active'] else "❌ Inactive"
            print(f"{r['name']} ({status})")
            print(f"  ID: {r['id']}")
            print(f"  Subdomain: {r['subdomain']}")
            print(f"  Slug: {r['slug']}")
            print(f"  Created: {r['created_at'].strftime('%Y-%m-%d %H:%M')}")
            print()
            
    finally:
        await conn.close()

def main():
    parser = argparse.ArgumentParser(description='Manage restaurants in the system')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add restaurant command
    add_parser = subparsers.add_parser('add', help='Add a new restaurant')
    add_parser.add_argument('--name', required=True, help='Restaurant name')
    add_parser.add_argument('--subdomain', required=True, help='Subdomain (e.g., "luigi" for luigi.restaurant-ai.com)')
    add_parser.add_argument('--slug', required=True, help='URL slug (e.g., "luigi" for /r/luigi)')
    add_parser.add_argument('--description', help='Restaurant description')
    add_parser.add_argument('--ai-name', default='Sophie', help='AI assistant name')
    add_parser.add_argument('--ai-personality', help='AI personality description')
    add_parser.add_argument('--welcome-message', help='Custom welcome message')
    add_parser.add_argument('--primary-color', default='#3498db', help='Primary theme color')
    add_parser.add_argument('--add-samples', action='store_true', help='Add sample menu items')
    
    # List restaurants command
    list_parser = subparsers.add_parser('list', help='List all restaurants')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        asyncio.run(add_restaurant(args))
    elif args.command == 'list':
        asyncio.run(list_restaurants())
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
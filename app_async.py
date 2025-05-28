#!/usr/bin/env python3
"""
Restaurant AI Application - Async Multi-Restaurant Version

Features:
- Async request handling with aiohttp
- Multi-restaurant support with URL routing
- PostgreSQL for data persistence
- Redis for caching
- Connection pooling for performance
"""

import asyncio
import aiohttp
from aiohttp import web
import asyncpg
import redis.asyncio as redis
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG') else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class RestaurantCache:
    """Redis cache manager for restaurant data"""
    
    def __init__(self, redis_pool):
        self.redis = redis_pool
        self.ttl = 3600  # 1 hour cache
    
    async def get_restaurant(self, restaurant_id: str) -> Optional[Dict]:
        """Get restaurant data from cache"""
        try:
            data = await self.redis.get(f"restaurant:{restaurant_id}")
            if data:
                logger.debug(f"Cache hit for restaurant {restaurant_id}")
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None
    
    async def set_restaurant(self, restaurant_id: str, data: Dict):
        """Cache restaurant data"""
        try:
            await self.redis.setex(
                f"restaurant:{restaurant_id}",
                self.ttl,
                json.dumps(data)
            )
            logger.debug(f"Cached restaurant {restaurant_id}")
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def get_menu(self, restaurant_id: str) -> Optional[List]:
        """Get menu from cache"""
        try:
            data = await self.redis.get(f"menu:{restaurant_id}")
            if data:
                logger.debug(f"Cache hit for menu {restaurant_id}")
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis menu get error: {e}")
        return None
    
    async def set_menu(self, restaurant_id: str, menu: List):
        """Cache menu data"""
        try:
            await self.redis.setex(
                f"menu:{restaurant_id}",
                self.ttl,
                json.dumps(menu)
            )
            logger.debug(f"Cached menu for {restaurant_id}")
        except Exception as e:
            logger.error(f"Redis menu set error: {e}")
    
    async def invalidate_restaurant(self, restaurant_id: str):
        """Invalidate restaurant cache"""
        try:
            await self.redis.delete(f"restaurant:{restaurant_id}")
            await self.redis.delete(f"menu:{restaurant_id}")
            logger.info(f"Invalidated cache for {restaurant_id}")
        except Exception as e:
            logger.error(f"Redis invalidate error: {e}")


class DatabaseManager:
    """PostgreSQL database manager"""
    
    def __init__(self, db_pool):
        self.pool = db_pool
    
    async def get_restaurant_by_subdomain(self, subdomain: str) -> Optional[Dict]:
        """Get restaurant by subdomain"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, name, subdomain, theme_config, ai_personality, 
                       ai_name, welcome_message, created_at
                FROM restaurants 
                WHERE subdomain = $1 AND active = true
                """,
                subdomain
            )
            
            if row:
                return dict(row)
            return None
    
    async def get_restaurant_by_slug(self, slug: str) -> Optional[Dict]:
        """Get restaurant by URL slug"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, name, subdomain, slug, theme_config, ai_personality,
                       ai_name, welcome_message, created_at
                FROM restaurants 
                WHERE slug = $1 AND active = true
                """,
                slug
            )
            
            if row:
                return dict(row)
            return None
    
    async def get_menu_items(self, restaurant_id: str) -> List[Dict]:
        """Get menu items for restaurant"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, name, description, price, category, ingredients,
                       allergens, vegetarian, vegan, gluten_free, spice_level,
                       prep_time, calories, chef_notes, image_url, display_order
                FROM menu_items 
                WHERE restaurant_id = $1 AND active = true
                ORDER BY display_order, category, name
                """,
                restaurant_id
            )
            
            return [dict(row) for row in rows]
    
    async def log_conversation(self, restaurant_id: str, session_id: str, 
                             message: str, response: str):
        """Log conversation to database"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO conversations 
                (restaurant_id, session_id, message, response, timestamp)
                VALUES ($1, $2, $3, $4, $5)
                """,
                restaurant_id, session_id, message, response, datetime.utcnow()
            )
    
    async def get_restaurant_stats(self, restaurant_id: str) -> Dict:
        """Get restaurant statistics"""
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_conversations,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    DATE(timestamp) as date
                FROM conversations
                WHERE restaurant_id = $1 
                    AND timestamp > CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                """,
                restaurant_id
            )
            
            return dict(stats) if stats else {}


class MultiRestaurantAI:
    """AI handler for multiple restaurants"""
    
    def __init__(self, db_manager: DatabaseManager, cache: RestaurantCache):
        self.db = db_manager
        self.cache = cache
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Determine AI service
        if self.openai_api_key:
            self.ai_service = 'openai'
            self.api_key = self.openai_api_key
        elif self.groq_api_key:
            self.ai_service = 'groq'
            self.api_key = self.groq_api_key
        else:
            self.ai_service = None
            logger.warning("No AI API keys found")
    
    def build_system_prompt(self, restaurant: Dict, menu_items: List[Dict]) -> str:
        """Build restaurant-specific system prompt"""
        # Format menu for context
        menu_text = "\n".join([
            f"- {item['name']}: {item['description']} (${item['price']:.2f}) "
            f"[Category: {item['category']}, Vegetarian: {item.get('vegetarian', False)}, "
            f"Vegan: {item.get('vegan', False)}, Gluten-free: {item.get('gluten_free', False)}]"
            for item in menu_items
        ])
        
        ai_name = restaurant.get('ai_name', 'Sophie')
        personality = restaurant.get('ai_personality', 'friendly and helpful')
        
        return f"""You are {ai_name}, the AI assistant for {restaurant['name']}. 
You are {personality}.

RESTAURANT MENU:
{menu_text}

GUIDELINES:
- Be warm and engaging but keep responses concise (10-20 words typically)
- Only mention prices when specifically asked
- Make personalized recommendations based on preferences
- Use emojis occasionally for warmth
- Always stay in character for {restaurant['name']}
"""
    
    async def generate_response(self, restaurant_id: str, message: str, 
                              session_id: str) -> Dict:
        """Generate AI response for restaurant"""
        logger.info(f"Generating response for restaurant {restaurant_id}: '{message}'")
        
        try:
            # Get restaurant data
            restaurant = await self.cache.get_restaurant(restaurant_id)
            if not restaurant:
                restaurant = await self.db.get_restaurant_by_subdomain(restaurant_id)
                if restaurant:
                    await self.cache.set_restaurant(restaurant_id, restaurant)
            
            if not restaurant:
                return {
                    'success': False,
                    'error': 'Restaurant not found'
                }
            
            # Get menu
            menu_items = await self.cache.get_menu(restaurant_id)
            if not menu_items:
                menu_items = await self.db.get_menu_items(restaurant['id'])
                if menu_items:
                    await self.cache.set_menu(restaurant_id, menu_items)
            
            # Generate response
            if self.ai_service:
                response_text = await self._call_ai_api(
                    self.build_system_prompt(restaurant, menu_items),
                    message
                )
            else:
                response_text = self._generate_fallback_response(message, restaurant)
            
            # Extract recommendations
            recommendations = self._extract_recommendations(response_text, menu_items)
            
            # Log conversation
            await self.db.log_conversation(
                restaurant['id'], session_id, message, response_text
            )
            
            return {
                'success': True,
                'response': response_text,
                'recommendations': recommendations,
                'restaurant': {
                    'name': restaurant['name'],
                    'ai_name': restaurant.get('ai_name', 'Sophie')
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to generate response'
            }
    
    async def _call_ai_api(self, system_prompt: str, message: str) -> str:
        """Call AI API asynchronously"""
        if self.ai_service == 'groq':
            url = "https://api.groq.com/openai/v1/chat/completions"
            model = "llama3-70b-8192"
        else:
            url = "https://api.openai.com/v1/chat/completions"
            model = "gpt-3.5-turbo"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "max_tokens": 80,
            "temperature": 0.8
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['choices'][0]['message']['content']
                else:
                    logger.error(f"AI API error: {resp.status}")
                    raise Exception(f"AI API error: {resp.status}")
    
    def _generate_fallback_response(self, message: str, restaurant: Dict) -> str:
        """Generate fallback response"""
        ai_name = restaurant.get('ai_name', 'Sophie')
        responses = [
            f"Hi! I'm {ai_name} from {restaurant['name']}. What can I help you find?",
            "Looking for something specific? I'd love to help!",
            "Our menu has some amazing options. What are you in the mood for?"
        ]
        return responses[hash(message) % len(responses)]
    
    def _extract_recommendations(self, response: str, menu_items: List[Dict]) -> List[Dict]:
        """Extract menu recommendations from response"""
        recommendations = []
        response_lower = response.lower()
        
        for item in menu_items:
            if item['name'].lower() in response_lower:
                recommendations.append({
                    'id': item['id'],
                    'name': item['name'],
                    'price': item['price'],
                    'description': item['description']
                })
                if len(recommendations) >= 2:
                    break
        
        return recommendations


class RestaurantWebApp:
    """Main web application"""
    
    def __init__(self):
        self.db_pool = None
        self.redis_pool = None
        self.db_manager = None
        self.cache = None
        self.ai_handler = None
    
    async def startup(self, app):
        """Initialize application resources"""
        logger.info("Starting Restaurant AI Application")
        
        # Create database pool
        self.db_pool = await asyncpg.create_pool(
            os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/restaurant_ai'),
            min_size=10,
            max_size=20
        )
        
        # Create Redis pool
        self.redis_pool = await redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379'),
            max_connections=10,
            decode_responses=True
        )
        
        # Initialize managers
        self.db_manager = DatabaseManager(self.db_pool)
        self.cache = RestaurantCache(self.redis_pool)
        self.ai_handler = MultiRestaurantAI(self.db_manager, self.cache)
        
        # Store in app for access in handlers
        app['db'] = self.db_manager
        app['cache'] = self.cache
        app['ai'] = self.ai_handler
        
        logger.info("Application initialized successfully")
    
    async def cleanup(self, app):
        """Cleanup resources"""
        logger.info("Shutting down application")
        
        if self.redis_pool:
            await self.redis_pool.aclose()
        
        if self.db_pool:
            await self.db_pool.close()
    
    def get_restaurant_from_request(self, request) -> tuple:
        """Extract restaurant identifier from request"""
        host = request.host.lower()
        path = request.path
        
        # Check subdomain routing (e.g., luigi.restaurant-ai.com)
        if '.' in host:
            subdomain = host.split('.')[0]
            if subdomain not in ['www', 'app', 'api']:
                return ('subdomain', subdomain)
        
        # Check path routing (e.g., restaurant-ai.com/luigi)
        if path.startswith('/r/'):
            parts = path.split('/')
            if len(parts) >= 3:
                return ('slug', parts[2])
        
        return (None, None)
    
    async def handle_index(self, request):
        """Serve restaurant-specific homepage"""
        route_type, identifier = self.get_restaurant_from_request(request)
        
        if not route_type:
            # Serve generic landing page
            return web.Response(text="Welcome to Restaurant AI", content_type='text/html')
        
        # Get restaurant data
        db = request.app['db']
        
        if route_type == 'subdomain':
            restaurant = await db.get_restaurant_by_subdomain(identifier)
        else:
            restaurant = await db.get_restaurant_by_slug(identifier)
        
        if not restaurant:
            return web.Response(text="Restaurant not found", status=404)
        
        # Serve restaurant-specific template
        # In production, use a template engine like jinja2
        # Read the template file
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index_clean.html')
        with open(template_path, 'r') as f:
            html = f.read()
        
        # Replace restaurant-specific values
        html = html.replace('AI Restaurant', restaurant['name'])
        html = html.replace('Sophie', restaurant.get('ai_name', 'Sophie'))
        
        # Add restaurant data for JavaScript
        restaurant_data = f"""
        <script>
            window.RESTAURANT_DATA = {{
                id: "{restaurant['id']}",
                name: "{restaurant['name']}",
                ai_name: "{restaurant.get('ai_name', 'Sophie')}",
                slug: "{restaurant['slug']}"
            }};
        </script>
        """
        
        # Insert before closing body tag
        html = html.replace('</body>', f'{restaurant_data}</body>')
        
        return web.Response(text=html, content_type='text/html')
    
    async def handle_menu(self, request):
        """Get restaurant menu"""
        route_type, identifier = self.get_restaurant_from_request(request)
        
        # Also check query parameter as fallback
        if not route_type:
            restaurant_id = request.query.get('restaurant_id')
            if restaurant_id:
                route_type = 'slug'
                identifier = restaurant_id
        
        if not route_type:
            return web.json_response({'success': False, 'error': 'Restaurant not specified'})
        
        db = request.app['db']
        cache = request.app['cache']
        
        # Get restaurant
        if route_type == 'subdomain':
            restaurant = await db.get_restaurant_by_subdomain(identifier)
        else:
            restaurant = await db.get_restaurant_by_slug(identifier)
        
        if not restaurant:
            return web.json_response({'success': False, 'error': 'Restaurant not found'})
        
        # Get menu (with caching)
        menu_items = await cache.get_menu(restaurant['id'])
        if not menu_items:
            menu_items = await db.get_menu_items(restaurant['id'])
            await cache.set_menu(restaurant['id'], menu_items)
        
        return web.json_response({
            'success': True,
            'restaurant': {
                'id': restaurant['id'],
                'name': restaurant['name']
            },
            'items': menu_items,
            'count': len(menu_items)
        })
    
    async def handle_chat(self, request):
        """Handle chat messages"""
        route_type, identifier = self.get_restaurant_from_request(request)
        
        # Also check request body for restaurant_id
        if not route_type:
            try:
                data = await request.json()
                restaurant_id = data.get('restaurant_id')
                if restaurant_id:
                    route_type = 'slug'
                    identifier = restaurant_id
                    # Put data back for later use
                    request['_json_data'] = data
            except:
                pass
        
        if not route_type:
            return web.json_response({'success': False, 'error': 'Restaurant not specified'})
        
        try:
            # Use cached data if available
            data = request.get('_json_data') or await request.json()
            message = data.get('message', '').strip()
            session_id = data.get('session_id', 'anonymous')
            
            if not message:
                return web.json_response({'success': False, 'error': 'Empty message'})
            
            # Get restaurant ID
            db = request.app['db']
            
            if route_type == 'subdomain':
                restaurant = await db.get_restaurant_by_subdomain(identifier)
            else:
                restaurant = await db.get_restaurant_by_slug(identifier)
            
            if not restaurant:
                return web.json_response({'success': False, 'error': 'Restaurant not found'})
            
            # Generate response
            ai = request.app['ai']
            response = await ai.generate_response(
                restaurant['id'], 
                message, 
                session_id
            )
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return web.json_response({
                'success': False,
                'error': 'Failed to process message'
            })
    
    async def handle_static(self, request):
        """Serve static files"""
        path = request.match_info['path']
        file_path = os.path.join('static', path)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return web.FileResponse(file_path)
        
        return web.Response(text="Not found", status=404)
    
    async def handle_health(self, request):
        """Health check endpoint"""
        try:
            # Check database connection
            async with self.db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            
            # Check Redis connection
            await self.redis_pool.ping()
            
            return web.json_response({
                'status': 'healthy',
                'services': {
                    'database': 'connected',
                    'redis': 'connected',
                    'ai': 'configured' if self.ai_handler.ai_service else 'fallback'
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return web.json_response({
                'status': 'unhealthy',
                'error': str(e)
            }, status=503)
    
    async def handle_stats(self, request):
        """Get restaurant statistics"""
        restaurant_id = request.match_info['restaurant_id']
        
        try:
            stats = await self.db_manager.get_restaurant_stats(restaurant_id)
            return web.json_response({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return web.json_response({
                'success': False,
                'error': 'Failed to get statistics'
            }, status=500)


def create_app():
    """Create and configure the application"""
    app = web.Application()
    webapp = RestaurantWebApp()
    
    # Set up startup/cleanup
    app.on_startup.append(webapp.startup)
    app.on_cleanup.append(webapp.cleanup)
    
    # Add routes
    app.router.add_get('/', webapp.handle_index)
    app.router.add_get('/r/{slug}', webapp.handle_index)
    app.router.add_get('/api/menu', webapp.handle_menu)
    app.router.add_post('/api/chat', webapp.handle_chat)
    app.router.add_get('/static/{path:.*}', webapp.handle_static)
    app.router.add_get('/health', webapp.handle_health)
    app.router.add_get('/api/stats/{restaurant_id}', webapp.handle_stats)
    
    return app


if __name__ == '__main__':
    # Run the application
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    
    logger.info(f"Starting server on port {port}")
    web.run_app(app, host='0.0.0.0', port=port)
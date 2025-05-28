#!/usr/bin/env python3
"""
Restaurant AI Application - Clean & Interactive Version

A streamlined restaurant app with an intelligent AI assistant that provides
warm, contextual responses based on menu information and general conversation.

Author: Principal Software Engineer
Date: 2024
Version: 2.0.0
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import logging
import mimetypes
import random
from datetime import datetime
import urllib.request
import urllib.parse
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG') else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('restaurant_ai.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("="*60)
logger.info("Restaurant AI Application Starting")
logger.info(f"Python Version: {sys.version}")
logger.info(f"Working Directory: {os.getcwd()}")
logger.info("="*60)

# Enhanced menu data with detailed information
MENU_DATA = [
    {
        'id': 1,
        'name': 'Grilled Atlantic Salmon',
        'description': 'Fresh Atlantic salmon with lemon herb butter, seasonal roasted vegetables, and wild rice pilaf',
        'price': 28.99,
        'category': 'main',
        'ingredients': ['Atlantic salmon', 'lemon', 'herbs', 'seasonal vegetables', 'wild rice'],
        'allergens': ['fish'],
        'vegetarian': False,
        'vegan': False,
        'gluten_free': True,
        'spice_level': 0,
        'prep_time': '20 minutes',
        'calories': 420,
        'chef_notes': 'Our most popular healthy option, rich in omega-3 fatty acids'
    },
    {
        'id': 2,
        'name': 'Thai Red Curry Bowl',
        'description': 'Authentic red curry with coconut milk, mixed vegetables, Thai basil, and jasmine rice',
        'price': 22.99,
        'category': 'main',
        'ingredients': ['red curry paste', 'coconut milk', 'vegetables', 'Thai basil', 'jasmine rice'],
        'allergens': ['coconut'],
        'vegetarian': True,
        'vegan': True,
        'gluten_free': True,
        'spice_level': 4,
        'prep_time': '15 minutes',
        'calories': 380,
        'chef_notes': 'Authentic Thai flavors with adjustable spice level'
    },
    {
        'id': 3,
        'name': 'Classic Caesar Salad',
        'description': 'Crisp romaine lettuce, house-made Caesar dressing, parmesan cheese, and garlic croutons',
        'price': 14.99,
        'category': 'appetizer',
        'ingredients': ['romaine lettuce', 'parmesan cheese', 'garlic croutons', 'Caesar dressing'],
        'allergens': ['dairy', 'gluten', 'eggs'],
        'vegetarian': True,
        'vegan': False,
        'gluten_free': False,
        'spice_level': 0,
        'prep_time': '10 minutes',
        'calories': 320,
        'chef_notes': 'A timeless classic with our signature house-made dressing'
    },
    {
        'id': 4,
        'name': 'Molten Chocolate Cake',
        'description': 'Warm chocolate cake with molten center, vanilla bean ice cream, and fresh berries',
        'price': 9.99,
        'category': 'dessert',
        'ingredients': ['dark chocolate', 'eggs', 'flour', 'vanilla ice cream', 'fresh berries'],
        'allergens': ['dairy', 'gluten', 'eggs'],
        'vegetarian': True,
        'vegan': False,
        'gluten_free': False,
        'spice_level': 0,
        'prep_time': '12 minutes',
        'calories': 480,
        'chef_notes': 'Best enjoyed immediately while the center is still molten'
    },
    {
        'id': 5,
        'name': 'Mediterranean Quinoa Bowl',
        'description': 'Quinoa with roasted vegetables, chickpeas, feta cheese, olives, and tahini dressing',
        'price': 18.99,
        'category': 'main',
        'ingredients': ['quinoa', 'roasted vegetables', 'chickpeas', 'feta cheese', 'olives', 'tahini'],
        'allergens': ['dairy', 'sesame'],
        'vegetarian': True,
        'vegan': False,
        'gluten_free': True,
        'spice_level': 1,
        'prep_time': '15 minutes',
        'calories': 350,
        'chef_notes': 'Packed with protein and Mediterranean flavors'
    },
    {
        'id': 6,
        'name': 'Artisan Bruschetta',
        'description': 'Toasted sourdough with fresh tomatoes, basil, garlic, and extra virgin olive oil',
        'price': 11.99,
        'category': 'appetizer',
        'ingredients': ['sourdough bread', 'tomatoes', 'basil', 'garlic', 'olive oil'],
        'allergens': ['gluten'],
        'vegetarian': True,
        'vegan': True,
        'gluten_free': False,
        'spice_level': 0,
        'prep_time': '8 minutes',
        'calories': 180,
        'chef_notes': 'Made with locally sourced tomatoes and fresh herbs'
    }
]

class IntelligentAI:
    """
    Intelligent AI Assistant for restaurant interactions.
    Uses real AI models to provide dynamic, contextual responses based on menu data.
    """
    
    def __init__(self):
        logger.debug("Initializing IntelligentAI class")
        self.conversation_history = []
        self.greeting_used = False
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        
        # Log API key status (masked)
        if self.openai_api_key:
            logger.info(f"OpenAI API key configured: {self.openai_api_key[:8]}...{self.openai_api_key[-4:]}")
        if self.groq_api_key:
            logger.info(f"Groq API key configured: {self.groq_api_key[:8]}...{self.groq_api_key[-4:]}")
        
        # Determine which AI service to use
        self.ai_service = None
        if self.openai_api_key:
            self.ai_service = 'openai'
            logger.info("Using OpenAI as AI service")
        elif self.groq_api_key:
            self.ai_service = 'groq'
            logger.info("Using Groq as AI service")
        
        self.use_ai_model = self.ai_service is not None
        
        # System prompt for AI model
        self.system_prompt = self._build_system_prompt()
        logger.debug(f"System prompt length: {len(self.system_prompt)} characters")
        
        if not self.use_ai_model:
            logger.warning("No AI API key found. Falling back to rule-based responses.")
            logger.info("To use AI responses, set one of these environment variables:")
            logger.info("  - OPENAI_API_KEY (for OpenAI GPT models)")
            logger.info("  - GROQ_API_KEY (for free Groq Cloud models)")
    
    def _build_system_prompt(self):
        """Build the system prompt for the AI model"""
        menu_text = "\n".join([
            f"- {item['name']}: {item['description']} (${item['price']:.2f}) "
            f"[Category: {item['category']}, Vegetarian: {item['vegetarian']}, "
            f"Vegan: {item['vegan']}, Gluten-free: {item['gluten_free']}, "
            f"Spice level: {item['spice_level']}/5, Calories: {item['calories']}]"
            for item in MENU_DATA
        ])
        
        return f"""You're Sophie, a warm and charming dining companion helping someone pick from our menu. Be brief but WARM and ENGAGING.

RESTAURANT MENU:
{menu_text}

PERSONALITY RULES:
- SHORT but WARM responses - aim for 10-20 words
- Always acknowledge their mood/request with enthusiasm
- Make connections - show you "get" what they want
- Use positive energy: "Oh!", "Yes!", "Perfect!", "Mmm"
- Add emojis occasionally: 😋 🔥 ✨ 👌
- Never mention prices unless asked
- Keep it conversational and fun

ENGAGEMENT STYLE:
- React to their energy
- Mirror their mood
- Make them feel heard
- Build excitement about food
- Ask follow-ups that show interest

EXAMPLES:
User: "I'm hungry"
You: "Oh, I feel you! Something filling or keeping it light?"

User: "Something spicy"
You: "Yes! 🔥 Thai curry brings the heat - you'll love it!"

User: "Vegetarian?"
You: "Absolutely! The quinoa bowl is fantastic - super satisfying!"

User: "What's good?"
You: "The salmon's incredible today! Or feeling adventurous?"

User: "I'm tired"
You: "Comfort food time! The mac & cheese is like a warm hug."

User: "Tell me more"
You: "It's this creamy coconut curry with perfect spice balance. Fresh veggies, aromatic herbs - total flavor bomb! Want ingredients?"

Remember: Connect first, suggest second. Make them smile!"""
    
    def generate_response(self, user_message):
        """
        Generate an intelligent response using AI models or fallback to rule-based responses.
        
        Args:
            user_message (str): User's question or message
            
        Returns:
            dict: Response with message and recommendations
        """
        logger.info(f"Generating response for user message: '{user_message}'")
        
        # Store conversation
        self.conversation_history.append({"role": "user", "content": user_message})
        logger.debug(f"Conversation history length: {len(self.conversation_history)}")
        
        if self.use_ai_model:
            logger.debug("Using AI model for response generation")
            return self._generate_ai_response(user_message)
        else:
            logger.debug("Using fallback rule-based response")
            return self._generate_fallback_response(user_message)
    
    def _generate_ai_response(self, user_message):
        """Generate response using AI API"""
        logger.debug(f"Generating AI response using {self.ai_service}")
        try:
            # Prepare conversation context
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add recent conversation history (last 6 messages to stay within token limits)
            recent_history = self.conversation_history[-6:]
            messages.extend(recent_history)
            logger.debug(f"Sending {len(messages)} messages to AI API")
            
            # Call AI API
            start_time = datetime.now()
            ai_response = self._call_openai_api(messages)
            response_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"AI API response received in {response_time:.2f} seconds")
            logger.debug(f"AI response: '{ai_response}'")
            
            # Extract recommended items from the response
            recommendations = self._extract_recommendations(ai_response)
            logger.debug(f"Extracted {len(recommendations)} recommendations")
            
            # Store AI response in conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return {
                'message': ai_response,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"AI API error: {str(e)}", exc_info=True)
            # Fallback to rule-based response
            logger.info("Falling back to rule-based response due to AI error")
            return self._generate_fallback_response(user_message)
    
    def _call_openai_api(self, messages):
        """Make API call to AI service (OpenAI or Groq)"""
        if self.ai_service == 'openai':
            url = "https://api.openai.com/v1/chat/completions"
            api_key = self.openai_api_key
            model = "gpt-3.5-turbo"
        elif self.ai_service == 'groq':
            url = "https://api.groq.com/openai/v1/chat/completions"
            api_key = self.groq_api_key
            model = "llama3-70b-8192"  # Powerful Llama 3 model from Groq
        else:
            raise ValueError("No AI service configured")
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": 80,  # Balanced for warm but brief responses
            "temperature": 0.8,  # Slightly higher for more personality
            "top_p": 0.9
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        req = urllib.request.Request(url, 
                                   data=json.dumps(data).encode('utf-8'),
                                   headers=headers,
                                   method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content'].strip()
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logger.error(f"AI API HTTP Error {e.code}: {error_body}")
            
            # Parse error details
            try:
                error_data = json.loads(error_body)
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                error_code = error_data.get('error', {}).get('code', 'unknown')
                logger.error(f"API Error Details - Code: {error_code}, Message: {error_msg}")
            except:
                logger.error(f"Raw error: {error_body}")
            
            raise
        except Exception as e:
            logger.error(f"AI API Error: {str(e)}")
            raise
    
    def _extract_recommendations(self, ai_response):
        """Extract menu item recommendations from AI response"""
        recommendations = []
        response_lower = ai_response.lower()
        
        # Find mentioned menu items
        for item in MENU_DATA:
            item_name_lower = item['name'].lower()
            # Check if the item name or key ingredients are mentioned
            if (item_name_lower in response_lower or 
                any(ingredient.lower() in response_lower for ingredient in item['ingredients'][:2])):
                recommendations.append(item)
                if len(recommendations) >= 2:  # Limit to 2 recommendations
                    break
        
        # If no specific items found, return featured items
        if not recommendations:
            recommendations = self._get_featured_items()[:2]
        
        return recommendations
    
    def _generate_fallback_response(self, user_message):
        """Generate rule-based response as fallback"""
        user_message_lower = user_message.lower().strip()
        
        # Determine response type
        if self._is_greeting(user_message_lower):
            return self._handle_greeting()
        elif self._is_menu_query(user_message_lower):
            return self._handle_menu_query(user_message_lower)
        elif self._is_dietary_query(user_message_lower):
            return self._handle_dietary_query(user_message_lower)
        elif self._is_recommendation_request(user_message_lower):
            return self._handle_recommendation_request(user_message_lower)
        elif self._is_specific_item_query(user_message_lower):
            return self._handle_specific_item_query(user_message_lower)
        else:
            return self._handle_general_conversation(user_message_lower)
    
    def _is_greeting(self, message):
        """Check if message is a greeting"""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in message for greeting in greetings)
    
    def _is_menu_query(self, message):
        """Check if message is asking about the menu"""
        menu_keywords = ['menu', 'dishes', 'food', 'eat', 'order', 'available', 'serve']
        return any(keyword in message for keyword in menu_keywords)
    
    def _is_dietary_query(self, message):
        """Check if message is about dietary preferences"""
        dietary_keywords = ['vegetarian', 'vegan', 'gluten', 'allergy', 'dairy', 'nuts']
        return any(keyword in message for keyword in dietary_keywords)
    
    def _is_recommendation_request(self, message):
        """Check if user is asking for recommendations"""
        rec_keywords = ['recommend', 'suggest', 'best', 'popular', 'hungry', 'mood', 'craving']
        return any(keyword in message for keyword in rec_keywords)
    
    def _is_specific_item_query(self, message):
        """Check if user is asking about a specific menu item"""
        for item in MENU_DATA:
            if item['name'].lower() in message or any(ingredient.lower() in message for ingredient in item['ingredients']):
                return True
        return False
    
    def _handle_greeting(self):
        """Handle greeting messages"""
        if not self.greeting_used:
            self.greeting_used = True
            responses = [
                "Hello! Welcome to our restaurant! I'm your AI dining assistant, here to help you discover delicious dishes that match your taste. What can I help you find today?",
                "Hi there! I'm excited to help you explore our menu and find something amazing to eat. Are you looking for something specific, or would you like me to suggest some popular options?",
                "Welcome! I'm here to make your dining experience special. Whether you're craving something specific or want to try something new, I'm here to help. What sounds good to you?"
            ]
        else:
            responses = [
                "Nice to see you again! What else can I help you with from our menu?",
                "How can I assist you further with your dining choices?",
                "What other questions do you have about our dishes?"
            ]
        
        return {
            'message': random.choice(responses),
            'recommendations': self._get_featured_items()
        }
    
    def _handle_menu_query(self, message):
        """Handle general menu questions"""
        if 'categories' in message or 'types' in message:
            categories = list(set(item['category'] for item in MENU_DATA))
            response = f"We offer dishes in these categories: {', '.join(categories)}. We have {len(MENU_DATA)} delicious options total. Would you like to explore any specific category?"
        elif 'price' in message or 'cost' in message:
            prices = [item['price'] for item in MENU_DATA]
            response = f"Our menu prices range from ${min(prices):.2f} to ${max(prices):.2f}. Most of our main courses are around $20-25. What's your budget range today?"
        else:
            response = f"Our menu features {len(MENU_DATA)} carefully crafted dishes, from appetizers to desserts. We have options for every dietary preference and taste. What type of food are you in the mood for?"
        
        return {
            'message': response,
            'recommendations': self._get_random_items(3)
        }
    
    def _handle_dietary_query(self, message):
        """Handle dietary restriction queries"""
        recommendations = []
        
        if 'vegetarian' in message:
            veg_items = [item for item in MENU_DATA if item['vegetarian']]
            response = f"We have {len(veg_items)} delicious vegetarian options! "
            recommendations = veg_items[:2]
        elif 'vegan' in message:
            vegan_items = [item for item in MENU_DATA if item['vegan']]
            response = f"We offer {len(vegan_items)} tasty vegan dishes! "
            recommendations = vegan_items[:2]
        elif 'gluten' in message:
            gf_items = [item for item in MENU_DATA if item['gluten_free']]
            response = f"We have {len(gf_items)} gluten-free options available! "
            recommendations = gf_items[:2]
        else:
            response = "I'd be happy to help with dietary preferences! We accommodate vegetarian, vegan, and gluten-free diets. We also list all allergens for each dish. What specific dietary needs do you have?"
            recommendations = self._get_random_items(2)
        
        if recommendations:
            rec_names = [item['name'] for item in recommendations]
            response += f"I especially recommend: {' and '.join(rec_names)}."
        
        return {
            'message': response,
            'recommendations': recommendations
        }
    
    def _handle_recommendation_request(self, message):
        """Handle recommendation requests"""
        recommendations = []
        
        if any(word in message for word in ['hungry', 'starving', 'filling']):
            # Recommend hearty main courses
            recommendations = [item for item in MENU_DATA if item['category'] == 'main' and item['calories'] > 350]
            response = "You sound really hungry! I recommend our hearty main courses that will definitely satisfy your appetite."
        elif any(word in message for word in ['light', 'small', 'not very hungry']):
            # Recommend appetizers or lighter options
            recommendations = [item for item in MENU_DATA if item['category'] == 'appetizer' or item['calories'] < 300]
            response = "For something light, our appetizers are perfect, or I can suggest some lighter main dishes."
        elif any(word in message for word in ['spicy', 'hot']):
            # Recommend spicy items
            recommendations = [item for item in MENU_DATA if item['spice_level'] > 2]
            response = "Looking for some heat? Our spicy dishes will definitely give you that kick you're craving!"
        elif any(word in message for word in ['healthy', 'nutritious', 'diet']):
            # Recommend healthy options
            recommendations = [item for item in MENU_DATA if item['calories'] < 400 or item['gluten_free']]
            response = "For healthy choices, I recommend our nutritious options that are both delicious and good for you."
        elif any(word in message for word in ['sweet', 'dessert']):
            # Recommend desserts
            recommendations = [item for item in MENU_DATA if item['category'] == 'dessert']
            response = "Our desserts are absolutely divine! Perfect way to end your meal on a sweet note."
        else:
            # General recommendations
            recommendations = self._get_popular_items()
            response = "I'd love to recommend some of our most popular dishes that guests absolutely love!"
        
        return {
            'message': response,
            'recommendations': recommendations[:2]
        }
    
    def _handle_specific_item_query(self, message):
        """Handle questions about specific menu items"""
        for item in MENU_DATA:
            if item['name'].lower() in message:
                response = f"Great choice! Our {item['name']} is {item['description']} It's priced at ${item['price']:.2f}."
                
                # Add specific details based on what they might be asking
                if 'ingredient' in message:
                    response += f" The main ingredients are: {', '.join(item['ingredients'])}."
                if 'allerg' in message:
                    response += f" Please note it contains: {', '.join(item['allergens'])}." if item['allergens'] else " This dish has no major allergens."
                if 'spicy' in message or 'hot' in message:
                    response += f" The spice level is {item['spice_level']} out of 5."
                if 'time' in message:
                    response += f" Preparation time is about {item['prep_time']}."
                
                return {
                    'message': response,
                    'recommendations': [item]
                }
        
        # If no specific item found, provide helpful response
        return {
            'message': "I'd be happy to tell you about any of our dishes! Could you be more specific about which item you're interested in, or would you like me to suggest something based on your preferences?",
            'recommendations': self._get_random_items(2)
        }
    
    def _handle_general_conversation(self, message):
        """Handle general conversation and out-of-menu queries"""
        # Friendly responses for general questions
        if any(word in message for word in ['how are you', 'how do you do']):
            responses = [
                "I'm doing great, thank you for asking! I'm excited to help you find something delicious to eat. What sounds good to you today?",
                "I'm wonderful, thanks! Ready to help you discover your next favorite dish. What are you in the mood for?"
            ]
        elif any(word in message for word in ['thank you', 'thanks']):
            responses = [
                "You're very welcome! I'm here whenever you need help with our menu. Anything else I can assist you with?",
                "My pleasure! I love helping people find great food. Is there anything else you'd like to know?"
            ]
        elif any(word in message for word in ['bye', 'goodbye', 'see you']):
            responses = [
                "Goodbye! I hope you enjoy your meal and have a wonderful dining experience. Come back anytime!",
                "Have a fantastic meal! It was great helping you today. See you next time!"
            ]
        else:
            # For other general questions, redirect warmly to menu
            responses = [
                "That's an interesting question! While I specialize in helping with our menu and dining recommendations, I'm always happy to chat. Speaking of food, is there anything from our menu I can help you with?",
                "I appreciate you asking! I'm here primarily to help you navigate our delicious menu options. What kind of flavors are you craving today?",
                "Thanks for sharing! I'd love to help you find something amazing to eat. Are you looking for any particular type of cuisine or dish?"
            ]
        
        return {
            'message': random.choice(responses),
            'recommendations': self._get_random_items(2)
        }
    
    def _get_featured_items(self):
        """Get featured menu items"""
        return MENU_DATA[:3]
    
    def _get_random_items(self, count=2):
        """Get random menu items"""
        return random.sample(MENU_DATA, min(count, len(MENU_DATA)))
    
    def _get_popular_items(self):
        """Get popular items (simulated based on price and ratings)"""
        # Simulate popularity based on balanced price and features
        popular = sorted(MENU_DATA, key=lambda x: x['calories'] + (30 - x['price']))
        return popular[:3]


class RestaurantHandler(SimpleHTTPRequestHandler):
    """Streamlined HTTP handler for the restaurant application"""
    
    # Class variable to share AI assistant across all requests
    ai_assistant = None
    
    def __init__(self, *args, **kwargs):
        # Initialize AI assistant only once at class level
        if RestaurantHandler.ai_assistant is None:
            RestaurantHandler.ai_assistant = IntelligentAI()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        logger.info(f"GET request: {self.path} from {self.client_address[0]}")
        
        if self.path == '/':
            self._serve_file('templates/index_clean.html', 'text/html')
        elif self.path.startswith('/api/menu'):
            self._serve_menu()
        elif self.path.startswith('/static/'):
            self._serve_static_file()
        else:
            logger.warning(f"404 Not Found: {self.path}")
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        logger.info(f"POST request: {self.path} from {self.client_address[0]}")
        
        if self.path == '/api/chat':
            self._handle_chat()
        else:
            logger.warning(f"404 Not Found: {self.path}")
            self.send_error(404, "Not Found")
    
    def _serve_file(self, filepath, content_type):
        """Serve a file with specified content type"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, f"File not found: {filepath}")
    
    def _serve_menu(self):
        """Serve menu data"""
        response = {
            'success': True,
            'items': MENU_DATA,
            'count': len(MENU_DATA)
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def _serve_static_file(self):
        """Serve static files"""
        file_path = self.path[8:]  # Remove '/static/'
        full_path = os.path.join('static', file_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            content_type, _ = mimetypes.guess_type(full_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            with open(full_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "File not found")
    
    def _handle_chat(self):
        """Handle AI chat requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            user_message = data.get('message', '').strip()
            if not user_message:
                raise ValueError("Empty message")
            
            # Generate AI response
            ai_response = RestaurantHandler.ai_assistant.generate_response(user_message)
            
            response = {
                'success': True,
                'response': ai_response['message'],
                'recommendations': ai_response['recommendations'],
                'context': {'timestamp': datetime.now().isoformat()}
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            error_response = {
                'success': False,
                'error': 'I apologize, but I encountered an issue. Could you please try rephrasing your question?'
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def log_message(self, format, *args):
        """Override to use custom logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")


def run_server(port=5000):
    """Run the restaurant server"""
    server_address = ('', port)
    
    # Check AI configuration
    if os.getenv('GROQ_API_KEY'):
        ai_status = "🤖 AI-Powered Assistant (Groq - FREE)"
    elif os.getenv('OPENAI_API_KEY'):
        ai_status = "🤖 AI-Powered Assistant (OpenAI)"
    else:
        ai_status = "🔧 Rule-Based Assistant"
    
    try:
        httpd = HTTPServer(server_address, RestaurantHandler)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use!")
            print(f"💡 Try one of these options:")
            print(f"   1. Kill the existing process: lsof -i :{port} then kill <PID>")
            print(f"   2. Use a different port: python3 app_clean.py --port 8080")
            return
        else:
            raise
    
    print(f"\n🍽️  Restaurant AI Application")
    print(f"📍 http://localhost:{port}")
    print(f"{ai_status} Ready")
    
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('GROQ_API_KEY'):
        print(f"💡 For AI-powered responses, run: python3 setup_ai.py")
    
    print(f"Press Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.shutdown()


if __name__ == '__main__':
    import sys
    
    # Simple argument parsing for port
    port = int(os.getenv('PORT', 5000))  # Support PORT env var for cloud platforms
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--port' and len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print(f"❌ Invalid port number: {sys.argv[2]}")
                sys.exit(1)
        else:
            print("Usage: python3 app_clean.py [--port PORT_NUMBER]")
            sys.exit(1)
    
    run_server(port)
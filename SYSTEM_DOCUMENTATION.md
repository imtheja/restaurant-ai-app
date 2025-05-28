# 📚 Restaurant AI - Complete System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Request Flow Diagrams](#request-flow-diagrams)
4. [Logging Architecture](#logging-architecture)
5. [API Documentation](#api-documentation)
6. [Configuration Guide](#configuration-guide)
7. [Deployment Guide](#deployment-guide)
8. [Troubleshooting](#troubleshooting)

## System Overview

The Restaurant AI application is a modern web application that provides an intelligent dining assistant through natural language processing. The system is designed with simplicity, scalability, and user experience in mind.

### Key Features
- **Natural Language Understanding**: AI-powered conversations about menu items
- **Speech Interface**: Voice input/output using Web Speech API
- **Real-time Recommendations**: Dynamic menu suggestions based on preferences
- **Zero Dependencies**: Built using Python standard library only
- **Multi-AI Support**: Works with Groq (free) or OpenAI (paid)

## Component Architecture

### Directory Structure
```
restaurant-ai-app/
├── app_clean.py              # Main application server
├── templates/
│   └── index_clean.html      # Single-page application HTML
├── static/
│   ├── css/
│   │   └── style_clean.css   # Application styling
│   └── js/
│       └── app_clean.js      # Frontend JavaScript
├── ARCHITECTURE.md           # System architecture details
├── SYSTEM_DOCUMENTATION.md   # This file
├── README.md                 # User-facing documentation
└── restaurant_ai.log         # Application logs
```

### Backend Components

#### 1. HTTP Server (`app_clean.py`)
```python
class RestaurantHandler(SimpleHTTPRequestHandler):
    """
    Main HTTP request handler
    - Routes requests to appropriate handlers
    - Serves static files
    - Manages API endpoints
    """
```

**Key Methods:**
- `do_GET()`: Handles all GET requests
- `do_POST()`: Handles all POST requests
- `_serve_file()`: Serves HTML templates
- `_serve_static_file()`: Serves CSS/JS files
- `_serve_menu()`: Returns menu data as JSON
- `_handle_chat()`: Processes chat messages

#### 2. AI Integration (`IntelligentAI` class)
```python
class IntelligentAI:
    """
    Manages AI interactions and responses
    - Integrates with external AI services
    - Maintains conversation context
    - Handles fallback logic
    """
```

**Key Methods:**
- `generate_response()`: Main entry point for generating responses
- `_generate_ai_response()`: Uses AI service for response
- `_generate_fallback_response()`: Rule-based fallback
- `_call_openai_api()`: Makes API calls to AI services
- `_extract_recommendations()`: Parses AI responses for menu items

### Frontend Components

#### 1. HTML Structure (`index_clean.html`)
- Single-page application
- Semantic HTML5 markup
- Responsive grid layout
- Modal system for item details

#### 2. JavaScript Logic (`app_clean.js`)
```javascript
// Application State Management
const AppState = {
    menuItems: [],        // All menu items
    filteredItems: [],    // Currently displayed items
    currentCategory: '',  // Active filter
    dietaryFilters: {},   // Dietary preferences
    isListening: false,   // Voice recognition state
    isSpeaking: false     // Speech synthesis state
}
```

**Key Functions:**
- `initializeSpeechRecognition()`: Sets up voice input
- `sendMessage()`: Sends chat messages to server
- `speakResponse()`: Converts text to speech
- `filterMenuItems()`: Client-side menu filtering
- `showMenuItem()`: Displays item details

## Request Flow Diagrams

### 1. Initial Page Load
```
Browser                     Server                      Response
   |                          |                            |
   |----GET /---------------->|                            |
   |                          |----index_clean.html------->|
   |<-------------------------|                            |
   |                          |                            |
   |----GET /static/css------>|                            |
   |<---------CSS-------------|                            |
   |                          |                            |
   |----GET /static/js------->|                            |
   |<----------JS-------------|                            |
   |                          |                            |
   |----GET /api/menu-------->|                            |
   |<-------Menu JSON---------|                            |
```

### 2. Chat Interaction Flow
```
User Input → Speech Recognition → Text
    ↓
JavaScript (sendMessage)
    ↓
POST /api/chat
    ↓
RestaurantHandler._handle_chat()
    ↓
IntelligentAI.generate_response()
    ↓
[AI Service] ← API Call → Groq/OpenAI
    ↓
Response Processing
    ↓
JSON Response → Client
    ↓
UI Update + Speech Synthesis
```

### 3. Voice Interaction Sequence
```
1. User clicks Sophie avatar (👩‍💼)
2. Microphone button appears
3. User clicks microphone → startListening()
4. Speech → Text conversion (Web Speech API)
5. Text sent to server
6. AI response received
7. Text → Speech conversion
8. Audio output to user
```

## Logging Architecture

### Log Configuration
```python
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG') else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(),          # Console output
        logging.FileHandler('restaurant_ai.log')  # File output
    ]
)
```

### Log Levels
- **DEBUG**: Detailed execution flow, API payloads
- **INFO**: Request handling, response times, general flow
- **WARNING**: 404s, fallbacks, missing configurations
- **ERROR**: API failures, exceptions, critical issues

### Key Logged Events
1. **Application Startup**
   ```
   INFO - Restaurant AI Application Starting
   INFO - Python Version: 3.x.x
   INFO - Working Directory: /path/to/app
   ```

2. **API Configuration**
   ```
   INFO - Groq API key configured: gsk_xKC15J...oMDt
   INFO - Using Groq as AI service
   ```

3. **Request Handling**
   ```
   INFO - GET request: /api/menu from 127.0.0.1
   INFO - POST request: /api/chat from 127.0.0.1
   ```

4. **AI Processing**
   ```
   INFO - Generating response for user message: 'I'm hungry'
   DEBUG - Sending 3 messages to AI API
   INFO - AI API response received in 1.23 seconds
   ```

## API Documentation

### GET /
**Purpose**: Serve main application  
**Response**: HTML content  
**Status**: 200 OK

### GET /api/menu
**Purpose**: Retrieve all menu items  
**Response**: 
```json
{
    "success": true,
    "items": [...],
    "count": 6
}
```

### POST /api/chat
**Purpose**: Process chat messages  
**Request**:
```json
{
    "message": "I'm looking for something spicy"
}
```
**Response**:
```json
{
    "success": true,
    "response": "Yes! 🔥 Thai curry brings the heat - you'll love it!",
    "recommendations": [...],
    "context": {
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

### GET /static/*
**Purpose**: Serve static assets (CSS, JS)  
**Response**: File content  
**Status**: 200 OK or 404 Not Found

## Configuration Guide

### Environment Variables
```bash
# AI Service Configuration (choose one)
export GROQ_API_KEY='gsk_...'      # Free Groq API
export OPENAI_API_KEY='sk-...'     # Paid OpenAI API

# Optional Configuration
export PORT=5000                    # Server port (default: 5000)
export DEBUG=true                   # Enable debug logging
```

### AI Service Selection Priority
1. OpenAI (if `OPENAI_API_KEY` is set)
2. Groq (if `GROQ_API_KEY` is set)
3. Fallback to rule-based responses

### Menu Configuration
Menu items are defined in `MENU_DATA` array in `app_clean.py`:
```python
MENU_DATA = [
    {
        'id': 1,
        'name': 'Grilled Atlantic Salmon',
        'description': '...',
        'price': 28.99,
        'category': 'main',
        # ... additional fields
    }
]
```

## Deployment Guide

### Local Development
```bash
# Basic run
python3 app_clean.py

# With API key
GROQ_API_KEY='your-key' python3 app_clean.py

# With debug logging
DEBUG=true GROQ_API_KEY='your-key' python3 app_clean.py
```

### Production Deployment

#### Docker
```bash
docker build -t restaurant-ai .
docker run -p 8080:8080 -e GROQ_API_KEY='your-key' restaurant-ai
```

#### Cloud Platforms
- **Replit**: Upload files, add secrets, click Run
- **Railway**: `railway up` with environment variables
- **Render**: Connect GitHub, add env vars, deploy
- **Vercel**: Use included `vercel.json` configuration

## Troubleshooting

### Common Issues

#### 1. No AI Responses
**Symptom**: Fallback to rule-based responses  
**Solution**: 
- Check API key is set: `echo $GROQ_API_KEY`
- Verify in logs: Look for "API key configured"
- Test connection: Check for HTTP errors in logs

#### 2. Speech Recognition Not Working
**Symptom**: Microphone button doesn't work  
**Solution**:
- Use HTTPS or localhost
- Check browser permissions
- Verify browser compatibility (Chrome/Edge recommended)

#### 3. Port Already in Use
**Symptom**: "Address already in use" error  
**Solution**:
```bash
# Find process
lsof -i :5000
# Kill it
kill -9 <PID>
# Or use different port
python3 app_clean.py --port 8080
```

#### 4. API Errors
**Symptom**: 403/401 errors in logs  
**Solution**:
- Regenerate API key
- Check rate limits
- Verify key format (Groq: gsk_*, OpenAI: sk-*)

### Debug Mode
Enable detailed logging:
```bash
DEBUG=true python3 app_clean.py
```

Check logs:
```bash
tail -f restaurant_ai.log
```

### Performance Monitoring

Key metrics to monitor:
- **API Response Time**: Should be < 3 seconds
- **Token Usage**: Limited to 80 tokens per response
- **Memory Usage**: Conversation history limited to 6 messages
- **Error Rate**: Check logs for API failures

## Security Considerations

1. **API Keys**: Never commit to version control
2. **Input Validation**: All user inputs are sanitized
3. **HTTPS**: Required for production (Web Speech API)
4. **Rate Limiting**: Implement for production use
5. **CORS**: Restricted to same-origin requests

## Future Enhancements

1. **Caching Layer**: Cache common AI responses
2. **Database Integration**: Persistent conversation history
3. **Multi-language Support**: i18n implementation
4. **Analytics Dashboard**: Usage metrics and insights
5. **Voice Customization**: Multiple voice options
6. **Order Integration**: Connect to ordering system

---

For additional support, check the logs first, then refer to the specific component documentation above.
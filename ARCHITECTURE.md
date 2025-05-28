# 🏗️ Restaurant AI Application - System Architecture

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Request Flow](#request-flow)
5. [Data Flow](#data-flow)
6. [API Endpoints](#api-endpoints)
7. [Technology Stack](#technology-stack)
8. [Security Considerations](#security-considerations)

## Overview

The Restaurant AI Application is a single-page web application that provides an intelligent dining assistant through natural language processing and speech interaction. The system uses a Python HTTP server backend with AI integration and a responsive web frontend.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Browser                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │
│  │   HTML/CSS  │  │ JavaScript  │  │ Web Speech  │  │  Fetch   │  │
│  │   (UI/UX)   │  │   (Logic)   │  │     API     │  │   API    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Python HTTP Server                           │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │
│  │   Request   │  │   Static    │  │     API     │  │ Template │  │
│  │   Handler   │  │   Server    │  │  Endpoints  │  │  Server  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘  │
│         │                                   │                        │
│         └───────────────┬───────────────────┘                       │
│                         ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    IntelligentAI Class                       │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │  • Conversation Management                                   │   │
│  │  • AI Model Integration (OpenAI/Groq)                       │   │
│  │  • Response Generation                                       │   │
│  │  • Menu Context Processing                                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS API Calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      External AI Services                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌─────────────────────────────────┐   │
│  │    Groq Cloud API   │    │      OpenAI API                 │   │
│  │  (llama3-70b-8192)  │    │    (gpt-3.5-turbo)             │   │
│  └─────────────────────┘    └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Components

#### **index_clean.html**
- Single-page application structure
- Semantic HTML5 markup
- Responsive grid layout
- Modal system for detailed views
- Accessibility features (ARIA labels)

#### **app_clean.js**
- **AppState**: Centralized state management
- **DOM**: Cached element references
- **Speech Recognition**: Web Speech API integration
- **Event Handlers**: User interaction management
- **API Client**: Fetch-based server communication
- **UI Updates**: Dynamic content rendering

#### **style_clean.css**
- CSS custom properties for theming
- Responsive grid system
- Animation keyframes
- Component-specific styling
- Mobile-first approach

### 2. Backend Components

#### **app_clean.py**
Main application file containing:

- **RestaurantHandler**: HTTP request handler
  - Route management
  - Static file serving
  - API endpoint handling
  - Error handling

- **IntelligentAI**: AI integration class
  - Conversation history management
  - AI service abstraction (OpenAI/Groq)
  - Response generation
  - Menu context injection
  - Fallback mechanisms

- **Menu Data**: In-memory restaurant menu
  - Structured item information
  - Dietary flags
  - Nutritional data
  - Chef recommendations

### 3. AI Integration Layer

- **System Prompt Engineering**: Context-aware prompts
- **Token Management**: Optimized for cost and performance
- **Error Handling**: Graceful fallback to rule-based responses
- **Response Processing**: Emoji handling, recommendation extraction

## Request Flow

### 1. Page Load Flow
```
Browser → GET / → RestaurantHandler → serve index_clean.html
Browser → GET /static/css/style_clean.css → serve CSS
Browser → GET /static/js/app_clean.js → serve JavaScript
Browser → GET /api/menu → serve menu data as JSON
```

### 2. Chat Interaction Flow
```
1. User clicks Sophie avatar → Shows microphone
2. User speaks → Web Speech API → Speech-to-text
3. JavaScript → POST /api/chat → RestaurantHandler
4. RestaurantHandler → IntelligentAI.generate_response()
5. IntelligentAI → AI Service API (Groq/OpenAI)
6. AI Response → Extract recommendations → Format response
7. Response → JavaScript → Update UI
8. Text-to-Speech → Sophie's voice → Audio output
```

### 3. Menu Interaction Flow
```
1. User clicks filter/item → JavaScript event
2. Update AppState → Filter menu items
3. Re-render menu grid → Update DOM
4. Click item → Show modal with details
```

## Data Flow

### 1. Menu Data Structure
```python
{
    'id': int,
    'name': str,
    'description': str,
    'price': float,
    'category': str,  # 'appetizer' | 'main' | 'dessert'
    'ingredients': List[str],
    'allergens': List[str],
    'vegetarian': bool,
    'vegan': bool,
    'gluten_free': bool,
    'spice_level': int,  # 0-5
    'prep_time': str,
    'calories': int,
    'chef_notes': str
}
```

### 2. API Request/Response Format

#### Chat Endpoint
**Request:**
```json
POST /api/chat
{
    "message": "I'm looking for something spicy"
}
```

**Response:**
```json
{
    "success": true,
    "response": "Yes! 🔥 Thai curry brings the heat - you'll love it!",
    "recommendations": [
        {
            "id": 2,
            "name": "Thai Red Curry Bowl",
            "price": 22.99,
            ...
        }
    ],
    "context": {
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

## API Endpoints

### GET /
- **Purpose**: Serve main application page
- **Response**: HTML content
- **Status Codes**: 200 (OK)

### GET /api/menu
- **Purpose**: Retrieve menu items
- **Response**: JSON array of menu items
- **Status Codes**: 200 (OK)

### POST /api/chat
- **Purpose**: Process chat messages
- **Request Body**: `{"message": "user input"}`
- **Response**: AI response with recommendations
- **Status Codes**: 200 (OK), 500 (Error)

### GET /static/*
- **Purpose**: Serve static assets
- **Response**: CSS/JS/Image files
- **Status Codes**: 200 (OK), 404 (Not Found)

## Technology Stack

### Backend
- **Language**: Python 3.6+
- **Framework**: Built-in HTTP server (no external dependencies)
- **AI Integration**: urllib for API calls
- **Data Format**: JSON

### Frontend
- **Languages**: HTML5, CSS3, JavaScript (ES6+)
- **APIs**: Web Speech API, Fetch API
- **Styling**: CSS Grid, Flexbox, Custom Properties
- **Icons**: Font Awesome

### AI Services
- **Primary**: Groq Cloud (Free tier)
  - Model: llama3-70b-8192
  - Endpoint: https://api.groq.com/openai/v1/chat/completions

- **Secondary**: OpenAI (Paid)
  - Model: gpt-3.5-turbo
  - Endpoint: https://api.openai.com/v1/chat/completions

## Security Considerations

### 1. API Key Management
- Environment variables for sensitive data
- Never exposed to client
- Server-side API calls only

### 2. Input Validation
- Message length limits
- Content sanitization
- XSS prevention

### 3. Rate Limiting
- Token limits per request
- Conversation history limits
- Error handling for API failures

### 4. HTTPS Requirements
- Required for Web Speech API
- Secure data transmission
- Certificate validation

### 5. CORS Policy
- Restricted to same origin
- No external domain access
- Controlled resource sharing

## Performance Optimizations

### 1. Frontend
- DOM element caching
- Event delegation
- Debounced API calls
- Efficient re-renders

### 2. Backend
- In-memory data storage
- Minimal dependencies
- Efficient routing
- Response caching potential

### 3. AI Integration
- Token optimization (80 max)
- Conversation history limits (6 messages)
- Fallback mechanisms
- Response time monitoring

## Error Handling

### 1. Client-Side
- Network error recovery
- Speech API fallbacks
- UI error states
- Console logging

### 2. Server-Side
- Try-catch blocks
- HTTP error codes
- Detailed logging
- Graceful degradation

### 3. AI Service
- API failure handling
- Fallback to rule-based
- Error message formatting
- Retry logic potential

## Deployment Considerations

### 1. Environment Variables
- `GROQ_API_KEY`: Primary AI service
- `OPENAI_API_KEY`: Secondary AI service
- `PORT`: Server port (default: 5000)

### 2. Platform Support
- Heroku: Procfile ready
- Docker: Containerizable
- Serverless: Adaptable
- Traditional hosting: Compatible

### 3. Scaling Considerations
- Stateless design
- Horizontal scaling ready
- CDN compatibility
- Load balancer friendly
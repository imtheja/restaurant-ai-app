# 🍽️ Restaurant AI - Your Food Buddy

A warm, conversational AI dining assistant that helps you discover delicious food through natural voice interaction.

## ✨ Features

- **👩‍💼 Sophie**: Your charming AI dining companion
- **🎙️ Natural Voice Interaction**: Speak naturally, interrupt anytime
- **💬 Warm Conversations**: Engaging, personalized responses
- **🎯 Smart Recommendations**: Based on your mood and preferences
- **📱 Responsive Design**: Works beautifully on all devices
- **📊 Comprehensive Logging**: Full system monitoring

## 🚀 Quick Start

### Option 1: With AI (Recommended)
```bash
# Get FREE Groq API key from: https://console.groq.com/keys
export GROQ_API_KEY='your-key-here'
python3 app_clean.py
```

### Option 2: Without AI
```bash
# Uses fallback responses
python3 app_clean.py
```

Open http://localhost:5000 in your browser.

## 💬 How to Use

1. **Click Sophie's avatar** 👩‍💼 to reveal microphone
2. **Click microphone** to start talking
3. **Speak naturally** - Sophie understands context
4. **Interrupt anytime** - Just start speaking
5. **Or type** if you prefer

## 📚 Documentation

- **[SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)** - Complete technical documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design
- **[FLOW_DIAGRAMS.md](FLOW_DIAGRAMS.md)** - Visual flow diagrams
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment options
- **[QUICKSTART.md](QUICKSTART.md)** - Detailed setup guide

## 🛠️ Technical Overview

- **Backend**: Python 3.6+ (zero dependencies)
- **AI**: Groq Cloud (free) or OpenAI (paid)
- **Frontend**: Vanilla JavaScript with Web Speech API
- **Architecture**: Client-server with AI integration
- **Logging**: Comprehensive request/response logging

## 📁 Project Structure

```
restaurant-ai-app/
├── app_clean.py              # Main server application
├── templates/
│   └── index_clean.html      # Single-page UI
├── static/
│   ├── css/
│   │   └── style_clean.css   # Styling
│   └── js/
│       └── app_clean.js      # Frontend logic
├── restaurant_ai.log         # Application logs
└── Documentation files...
```

## 🔧 Configuration

### Environment Variables
```bash
# AI Service (choose one)
export GROQ_API_KEY='gsk_...'      # Free
export OPENAI_API_KEY='sk-...'     # Paid

# Optional
export PORT=5000                    # Server port
export DEBUG=true                   # Enable debug logging
```

### Logging
- Logs to console and `restaurant_ai.log`
- Configurable log levels (INFO/DEBUG)
- Request tracking and performance metrics

## 🎯 Example Conversations

- "Hey Sophie, what's good today?"
- "I'm really hungry"
- "Something healthy please"
- "Tell me about the salmon"
- "I want comfort food"

Sophie responds with warmth and personality while keeping answers concise.

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment options:
- Replit (easiest)
- Railway
- Render
- Docker
- Vercel

---

Built with ❤️ for amazing dining experiences
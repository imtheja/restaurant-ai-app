# 🚀 Quick Start Guide - Restaurant AI with Real AI Models

## Option 1: FREE AI with Groq (Recommended)

### Step 1: Get a FREE Groq API Key
1. Visit: https://console.groq.com/keys
2. Sign up for a free account (no credit card required)
3. Click "Create API Key"
4. Copy your API key (starts with `gsk_`)

### Step 2: Set Your API Key
```bash
export GROQ_API_KEY='gsk_YOUR_KEY_HERE'
```

### Step 3: Run the App
```bash
python3 app_clean.py
```

### Step 4: Test AI Responses
1. Open http://localhost:5000
2. Click the microphone button
3. Say: "I'm looking for something spicy"
4. Listen to the AI's intelligent response!

---

## Option 2: OpenAI (Paid)

### Step 1: Get OpenAI API Key
1. Visit: https://platform.openai.com/api-keys
2. Create account and add payment method
3. Generate API key (starts with `sk-`)

### Step 2: Set Your API Key
```bash
export OPENAI_API_KEY='sk-YOUR_KEY_HERE'
```

### Step 3: Run the App
```bash
python3 app_clean.py
```

---

## Option 3: Interactive Setup

Run the setup wizard:
```bash
python3 setup_ai.py
```

This will guide you through the process step-by-step.

---

## Option 4: Demo Mode (No API Key)

For testing without an API key:
```bash
python3 demo_ai.py
# Select option 3 for Mock AI mode
```

---

## 🎤 Testing the AI Avatar

Once running with an AI key, try these phrases:
- "Hello, what do you recommend?"
- "I'm vegetarian, what options do you have?"
- "I want something healthy"
- "Tell me about the salmon"
- "I'm really hungry"
- "What's good for someone on a diet?"

The AI will provide intelligent, contextual responses based on the menu!

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Use a different port
python3 app_clean.py --port 8080
```

### API Key Not Working
```bash
# Test your connection
python3 setup_ai.py test
```

### No AI Responses
- Check that your API key is set correctly
- Ensure you have internet connection
- Verify the API key is valid

---

## 💡 Pro Tips

1. **Groq is FREE**: Perfect for testing and development
2. **Speech Works Best**: The app is optimized for voice interaction
3. **Context Matters**: The AI remembers your conversation history
4. **Try Different Moods**: Tell the AI how you're feeling for personalized suggestions

---

## 🎯 Example Session

```
You: "Hi, I'm looking for something comforting"
AI: "Welcome! For comfort food, I highly recommend our Molten Chocolate Cake...
     or if you prefer something savory, the Grilled Atlantic Salmon..."

You: "I'm vegetarian actually"
AI: "Perfect! In that case, our Thai Red Curry Bowl would be ideal...
     It's completely vegan and packed with comforting flavors..."

You: "That sounds good, tell me more"
AI: "Our Thai Red Curry Bowl features authentic red curry with coconut milk...
     It has a spice level of 4 out of 5, takes about 15 minutes..."
```

The AI provides natural, contextual responses that understand your preferences!
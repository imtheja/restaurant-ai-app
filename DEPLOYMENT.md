# 🚀 Deployment Guide - Restaurant AI App

## Option 1: Replit (Easiest - FREE)

### Steps:
1. Go to [replit.com](https://replit.com) and sign up
2. Click "Create Repl" → Import from GitHub/Upload
3. Upload these files:
   - `app_clean.py`
   - `templates/index_clean.html`
   - `static/css/style_clean.css`
   - `static/js/app_clean.js`
4. Set your secret (Secrets tab):
   ```
   GROQ_API_KEY = your_groq_key_here
   ```
5. Click "Run" - Replit will give you a public URL!

**Your friends can access:** `https://your-app-name.your-username.repl.co`

## Option 2: Railway (Professional - FREE tier)

### Steps:
1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Deploy:
   ```bash
   cd restaurant-ai-app
   railway login
   railway init
   railway up
   ```

3. Set environment variable:
   ```bash
   railway variables set GROQ_API_KEY=your_key_here
   ```

4. Get your URL:
   ```bash
   railway open
   ```

## Option 3: Render (Easy - FREE tier)

### Steps:
1. Create account at [render.com](https://render.com)
2. New → Web Service → Build from Git repo
3. Connect your GitHub (or use public Git URL)
4. Configure:
   - **Build Command**: `pip install -r requirements-simple.txt`
   - **Start Command**: `python app_clean.py`
5. Add environment variable:
   - `GROQ_API_KEY` = your key
6. Deploy!

## Option 4: Ngrok (Quick Testing - FREE)

### For quick sharing without deployment:
1. Install ngrok:
   ```bash
   brew install ngrok  # Mac
   # or download from ngrok.com
   ```

2. Run your app locally:
   ```bash
   GROQ_API_KEY='your_key' python3 app_clean.py
   ```

3. In another terminal:
   ```bash
   ngrok http 5000
   ```

4. Share the ngrok URL with friends!

## Option 5: Google Cloud Run (Scalable - Pay per use)

### Steps:
1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY . .
   EXPOSE 8080
   CMD ["python", "app_clean.py"]
   ```

2. Deploy:
   ```bash
   gcloud run deploy restaurant-ai \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GROQ_API_KEY=your_key
   ```

## Option 6: Vercel (Modern - FREE)

### Steps:
1. Create `requirements.txt`:
   ```
   # Empty - using standard library
   ```

2. Create `vercel.json`:
   ```json
   {
     "builds": [
       {"src": "app_clean.py", "use": "@vercel/python"}
     ],
     "routes": [
       {"src": "/(.*)", "dest": "app_clean.py"}
     ]
   }
   ```

3. Deploy:
   ```bash
   npm i -g vercel
   vercel
   ```

## 🔒 Security Tips

1. **API Key Protection**:
   - Never commit API keys to Git
   - Use environment variables
   - Consider using a proxy server for production

2. **Rate Limiting**:
   - Add request limiting to prevent abuse
   - Monitor API usage

3. **HTTPS Only**:
   - All platforms above provide HTTPS
   - Required for microphone access

## 📱 Sharing with Friends

Once deployed, share:
- The URL (e.g., `https://your-restaurant-ai.repl.co`)
- Tell them to:
  1. Click Sophie's avatar 👩‍💼
  2. Allow microphone access
  3. Start chatting!

## 🎯 Recommended: Start with Replit

For quick sharing with friends, Replit is the easiest:
1. No command line needed
2. Free hosting
3. Easy secret management
4. Instant public URL
5. Built-in editor for updates

---

## Quick Replit Setup

1. Go to: https://replit.com/new/python3
2. Drag and drop your files
3. Add secret: GROQ_API_KEY
4. Click Run
5. Share the URL!

Your app will be live in under 5 minutes! 🎉
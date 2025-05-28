# 🚀 Restaurant AI - Async Multi-Restaurant Edition

Production-ready async implementation with multi-restaurant support, PostgreSQL, and Redis caching.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer                             │
│                   (nginx/HAProxy)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┬─────────────────┐
         │                           │                   │
    ┌────▼─────┐              ┌─────▼────┐       ┌─────▼────┐
    │  App-1   │              │  App-2   │       │  App-N   │
    │ (aiohttp)│              │ (aiohttp)│       │ (aiohttp)│
    └────┬─────┘              └─────┬────┘       └─────┬────┘
         │                           │                   │
         └───────────┬───────────────┴───────────────────┘
                     │
         ┌───────────┴───────────┬─────────────────┐
         │                       │                 │
    ┌────▼────┐            ┌────▼────┐      ┌────▼────┐
    │PostgreSQL│            │  Redis  │      │ AI APIs │
    │ Primary  │            │ Cluster │      │ (Groq)  │
    └─────────┘            └─────────┘      └─────────┘
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository>
cd restaurant-ai-app
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start with Docker Compose
```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- pgAdmin on port 5050
- Redis Commander on port 8081
- Restaurant AI on port 8080

### 3. Initialize Database
```bash
docker-compose exec postgres psql -U restaurant_user -d restaurant_ai -f /docker-entrypoint-initdb.d/01-schema.sql
```

### 4. Add a Restaurant
```bash
python scripts/add_restaurant.py add \
  --name "Luigi's Bistro" \
  --subdomain "luigi" \
  --slug "luigi" \
  --add-samples
```

### 5. Access Your Restaurant
- Subdomain: http://luigi.localhost:8080
- Path: http://localhost:8080/r/luigi

## 📁 Project Structure

```
restaurant-ai-app/
├── app_async.py              # Async application with connection pooling
├── database/
│   └── schema.sql           # PostgreSQL schema
├── scripts/
│   └── add_restaurant.py    # Restaurant management
├── requirements-async.txt    # Python dependencies
├── docker-compose.yml       # Full stack setup
├── Dockerfile.async         # Production container
└── .env.example            # Environment template
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/restaurant_ai

# Redis
REDIS_URL=redis://localhost:6379

# AI Services
GROQ_API_KEY=gsk_your_key
OPENAI_API_KEY=sk_your_key

# Application
PORT=8080
APP_DOMAIN=restaurant-ai.com
```

## 🏢 Multi-Restaurant Features

### 1. URL-Based Routing
- **Subdomain**: `luigi.restaurant-ai.com`
- **Path**: `restaurant-ai.com/r/luigi`

### 2. Restaurant Isolation
- Separate menu data
- Custom AI personality
- Individual theming
- Analytics per restaurant

### 3. Caching Strategy
- Restaurant config: 1 hour TTL
- Menu items: 1 hour TTL
- Automatic invalidation on updates

## 📊 Performance Features

### Async Architecture
- **Concurrent Requests**: Handles 1000s simultaneously
- **Connection Pooling**: Database and Redis pools
- **Non-blocking I/O**: All operations are async

### Caching
- **Redis**: Restaurant configs and menus
- **TTL**: 1-hour default
- **Invalidation**: Automatic on updates

### Database Optimization
- **Indexes**: On all lookup fields
- **Connection Pool**: 10-20 connections
- **Read Replicas**: Analytics support

## 📈 Monitoring & Analytics

### Health Check
```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ai": "configured"
  }
}
```

### Restaurant Statistics
```bash
curl http://localhost:8080/api/stats/{restaurant_id}
```

## 🚀 Production Deployment

### 1. Using Gunicorn
```bash
gunicorn app_async:create_app \
  --bind 0.0.0.0:8080 \
  --worker-class aiohttp.GunicornWebWorker \
  --workers 4 \
  --worker-connections 1000
```

### 2. With Nginx
```nginx
upstream restaurant_ai {
    least_conn;
    server app1:8080;
    server app2:8080;
    server app3:8080;
}

server {
    server_name *.restaurant-ai.com;
    
    location / {
        proxy_pass http://restaurant_ai;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: restaurant-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: restaurant-ai
  template:
    metadata:
      labels:
        app: restaurant-ai
    spec:
      containers:
      - name: app
        image: restaurant-ai:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## 🔒 Security Considerations

1. **API Keys**: Store in environment variables
2. **Database**: Use connection pooling with SSL
3. **Redis**: Enable password authentication
4. **HTTPS**: Required for production
5. **Rate Limiting**: Implement per-restaurant limits

## 📊 Scaling Strategies

### Horizontal Scaling
- Add more app instances behind load balancer
- Use Redis for session sharing
- Database read replicas for analytics

### Vertical Scaling
- Increase worker connections
- Tune PostgreSQL for more connections
- Use Redis cluster for larger cache

### Database Sharding
- Shard by restaurant_id
- Separate analytics database
- Use connection pooling

## 🛠️ Management Scripts

### Add Restaurant
```bash
python scripts/add_restaurant.py add \
  --name "Restaurant Name" \
  --subdomain "subdomain" \
  --slug "url-slug" \
  --ai-name "Assistant Name" \
  --add-samples
```

### List Restaurants
```bash
python scripts/add_restaurant.py list
```

## 🐛 Troubleshooting

### Connection Pool Exhausted
- Increase pool size in `create_pool()`
- Check for connection leaks
- Monitor active connections

### Slow Responses
- Check Redis hit rate
- Analyze database queries
- Monitor AI API latency

### Memory Issues
- Limit conversation history
- Implement cache eviction
- Use connection pooling

## 📚 API Documentation

### Endpoints
- `GET /` - Restaurant homepage
- `GET /r/{slug}` - Restaurant by slug
- `GET /api/menu` - Get menu items
- `POST /api/chat` - Chat with AI
- `GET /health` - Health check
- `GET /api/stats/{id}` - Restaurant stats

### WebSocket Support (Future)
- Real-time chat updates
- Live order tracking
- Push notifications

---

Built for scale, speed, and multi-restaurant success! 🚀
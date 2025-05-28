# Docker Troubleshooting Guide

## Common Issues and Solutions

### 1. Port Already in Use

**Error**: `Bind for 0.0.0.0:XXXX failed: port is already allocated`

**Solution**:
```bash
# Find what's using the port (e.g., 5050)
lsof -i :5050

# Kill the process using the port
kill -9 <PID>

# Or change the port in docker-compose.yml
```

Current port mappings:
- 5432 → PostgreSQL
- 5051 → pgAdmin (changed from 5050)
- 6379 → Redis
- 8080 → Restaurant AI App
- 8082 → Redis Commander (changed from 8081)

### 2. Platform Warnings (ARM64 vs AMD64)

**Warning**: `The requested image's platform (linux/amd64) does not match the detected host platform`

**Solution**: Already fixed in docker-compose.yml with `platform: linux/amd64` for pgAdmin and Redis Commander.

### 3. Package Version Conflicts

**Error**: `aioredis==2.0.1` not found or deprecated

**Solution**: Updated to use `redis[hiredis]==5.0.1` with async support.

### 4. Database Connection Issues

**Error**: Connection to PostgreSQL failed

**Solutions**:
```bash
# Check if PostgreSQL is running
docker compose ps

# View PostgreSQL logs
docker compose logs postgres

# Restart PostgreSQL
docker compose restart postgres

# Connect manually to debug
docker exec -it restaurant_ai_postgres psql -U restaurant_user -d restaurant_ai
```

### 5. Redis Connection Issues

**Error**: Redis connection failed

**Solutions**:
```bash
# Check Redis status
docker compose ps redis

# Test Redis connection
docker exec -it restaurant_ai_redis redis-cli ping

# View Redis logs
docker compose logs redis
```

### 6. Application Not Starting

**Solutions**:
```bash
# View application logs
docker compose logs app

# Check if all environment variables are set
cat .env

# Rebuild the application
docker compose build app
docker compose up -d app
```

### 7. Clean Restart

If you need a completely fresh start:
```bash
# Stop and remove everything
docker compose down -v

# Remove all images
docker compose down --rmi all

# Clean Docker system
docker system prune -a

# Start fresh
./docker-deploy.sh
```

### 8. Memory Issues

If containers are crashing due to memory:
```bash
# Check Docker memory allocation
docker system info | grep Memory

# Increase Docker Desktop memory allocation in settings
# Recommended: At least 4GB for this stack
```

### 9. Checking Service Health

```bash
# Check all services
docker compose ps

# Health check endpoint
curl http://localhost:8080/health

# View detailed health status
docker inspect restaurant_ai_app | grep -A 10 Health
```

### 10. API Key Issues

Ensure your .env file contains valid API keys:
```bash
# Check if .env exists
ls -la .env

# Verify API keys are loaded
docker compose exec app env | grep -E 'OPENAI|GROQ'
```

## Quick Diagnostics Script

```bash
#!/bin/bash
echo "=== Docker Diagnostics ==="
echo "1. Docker version:"
docker --version
echo
echo "2. Docker Compose version:"
docker compose version
echo
echo "3. Running containers:"
docker compose ps
echo
echo "4. Port usage:"
for port in 5432 5051 6379 8080 8082; do
    echo -n "Port $port: "
    lsof -i :$port >/dev/null 2>&1 && echo "IN USE" || echo "FREE"
done
echo
echo "5. Recent logs:"
docker compose logs --tail=10
```

Save this as `diagnose.sh` and run with `bash diagnose.sh`.
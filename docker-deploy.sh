#!/bin/bash
#
# Docker deployment script for Restaurant AI Application
#
# This script cleanly deploys the async multi-restaurant version
# with PostgreSQL and Redis support

set -e

echo "=== Restaurant AI Docker Deployment ==="
echo

# Step 1: Stop and remove existing containers
echo "Step 1: Cleaning up existing containers..."
docker compose down -v 2>/dev/null || true
echo "✓ Cleanup complete"
echo

# Step 2: Check for port conflicts
echo "Step 2: Checking for port conflicts..."
for port in 5432 5051 6379 8080 8082; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  WARNING: Port $port is already in use"
        echo "   You may need to stop the service using this port or change the port in docker-compose.yml"
    fi
done
echo "✓ Port check complete"
echo

# Step 3: Create necessary directories
echo "Step 3: Creating necessary directories..."
mkdir -p database
echo "✓ Directories created"
echo

# Step 4: Build and start services
echo "Step 4: Starting services..."
echo "This may take a few minutes on first run..."
docker compose up -d --build

# Step 5: Wait for services to be healthy
echo
echo "Step 5: Waiting for services to be healthy..."
attempts=0
max_attempts=30

while [ $attempts -lt $max_attempts ]; do
    if docker compose ps | grep -q "healthy"; then
        echo "✓ Services are healthy!"
        break
    fi
    echo -n "."
    sleep 2
    attempts=$((attempts + 1))
done

if [ $attempts -eq $max_attempts ]; then
    echo
    echo "⚠️  WARNING: Services did not become healthy in time"
    echo "Check logs with: docker compose logs"
fi

echo
echo "=== Deployment Complete ==="
echo
echo "Services running at:"
echo "  - Restaurant AI App: http://localhost:8080"
echo "  - pgAdmin: http://localhost:5051 (admin@restaurant.ai / admin)"
echo "  - Redis Commander: http://localhost:8082"
echo
echo "Useful commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop services: docker compose down"
echo "  - View service status: docker compose ps"
echo
echo "To access different restaurants:"
echo "  - Default: http://localhost:8080"
echo "  - Luigi's: http://localhost:8080/r/luigi"
echo "  - Sakura: http://localhost:8080/r/sakura"
#!/bin/bash
#
# Kill processes on specific ports for Restaurant AI
#

echo "=== Killing processes on conflicting ports ==="
echo

# Function to kill process on a specific port
kill_port() {
    local port=$1
    echo "Checking port $port..."
    
    # Find PID using lsof
    local pid=$(lsof -ti :$port)
    
    if [ -n "$pid" ]; then
        # Get process info
        local process_info=$(ps -p $pid -o comm=,pid=,user= 2>/dev/null || echo "Unknown process")
        echo "  Found: $process_info"
        echo "  Killing PID $pid..."
        
        # Try graceful termination first
        kill -TERM $pid 2>/dev/null
        sleep 2
        
        # Check if still running
        if kill -0 $pid 2>/dev/null; then
            echo "  Process didn't terminate, forcing kill..."
            kill -9 $pid 2>/dev/null
        fi
        
        echo "  ✓ Port $port cleared"
    else
        echo "  ✓ Port $port is free"
    fi
    echo
}

# Kill processes on our ports
for port in 5051 8080 5432 6379 8082; do
    kill_port $port
done

# Also stop any running Docker containers that might be using these ports
echo "Stopping any running Docker containers..."
docker ps -q | xargs -r docker stop 2>/dev/null || true
docker ps -aq | xargs -r docker rm 2>/dev/null || true

echo
echo "=== All ports cleared ==="
echo "You can now run: ./docker-deploy.sh"
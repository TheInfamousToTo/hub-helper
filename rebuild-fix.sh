#!/bin/bash

echo "Rebuilding Hub Helper with analytics fixes..."

# Stop existing container
echo "Stopping existing container..."
docker-compose down

# Rebuild the image
echo "Rebuilding image..."
docker-compose build --no-cache

# Start the container
echo "Starting container..."
docker-compose up -d

# Show logs
echo "Container started. Showing logs..."
docker-compose logs -f --tail=20

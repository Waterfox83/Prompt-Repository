#!/bin/bash

# Docker Run Script for Prompt Repository
# This script helps you run the dockerized backend with local Qdrant

echo "================================================================"
echo "Prompt Repository - Docker Setup"
echo "================================================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your credentials:"
        echo "   - AWS credentials (for S3 access)"
        echo "   - GEMINI_API_KEY (for AI generation)"
        echo ""
        echo "Then run this script again."
        exit 1
    else
        echo "❌ .env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build and start containers
echo "Building and starting containers..."
docker-compose up --build -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start containers"
    exit 1
fi

echo ""
echo "================================================================"
echo "🎉 Containers Started Successfully!"
echo "================================================================"
echo ""
echo "Services:"
echo "  - Backend API: http://localhost:8000"
echo "  - Qdrant UI:   http://localhost:6333/dashboard"
echo ""
echo "Useful Commands:"
echo "  - View logs:        docker-compose logs -f"
echo "  - View backend:     docker-compose logs -f backend"
echo "  - View qdrant:      docker-compose logs -f qdrant"
echo "  - Stop containers:  docker-compose down"
echo "  - Restart:          docker-compose restart"
echo ""
echo "To stop and remove all data:"
echo "  docker-compose down -v"
echo "================================================================"

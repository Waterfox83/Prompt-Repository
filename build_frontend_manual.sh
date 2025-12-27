#!/bin/bash

# Check for API URL argument
if [ -z "$1" ]; then
    echo "⚠️  No API URL provided."
    echo "   Usage: ./build_frontend_manual.sh <YOUR_BACKEND_API_URL>"
    echo "   Example: ./build_frontend_manual.sh https://xyz.lambda-url.us-east-1.on.aws"
    echo ""
    read -p "Enter your Backend API URL (or press Enter to use localhost): " USER_URL
    
    if [ -z "$USER_URL" ]; then
        echo "Using default: http://127.0.0.1:8000"
    else
        export VITE_API_URL="$USER_URL"
    fi
else
    export VITE_API_URL="$1"
fi

echo "------------------------------------------------"
echo "Building frontend with API URL: ${VITE_API_URL:-http://127.0.0.1:8000}"
echo "------------------------------------------------"

cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Running build..."
npm run build

if [ $? -eq 0 ]; then
    echo "------------------------------------------------"
    echo "✅ Build complete!"
    echo "The build files are located in: frontend/dist"
    echo ""
    echo "ACTION REQUIRED:"
    echo "1. Go to your AWS S3 Console."
    echo "2. Open the bucket: pega-ai-prompt-repository"
    echo "3. Upload the CONTENTS of the 'frontend/dist' folder."
    echo "------------------------------------------------"
else
    echo "❌ Build failed."
    exit 1
fi

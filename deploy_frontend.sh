#!/bin/bash

# Configuration
BUCKET_NAME="pega-ai-prompt-repository"
DIST_DIR="frontend/dist"

# Check for API URL argument
if [ -z "$1" ]; then
    echo "⚠️  No API URL provided. The frontend will default to http://127.0.0.1:8000"
    echo "   To point to a production backend, run: ./deploy_frontend.sh <YOUR_BACKEND_API_URL>"
    echo "   Example: ./deploy_frontend.sh https://xyz.lambda-url.us-east-1.on.aws"
    echo "   Proceeding with default (localhost)..."
    read -p "Press Enter to continue or Ctrl+C to cancel..."
else
    export VITE_API_URL="$1"
    echo "✅ Setting API URL to: $VITE_API_URL"
fi

# 0. Check AWS Credentials
echo "Checking AWS credentials..."
aws sts get-caller-identity > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ AWS credentials invalid or expired. Please run 'aws sso login' or export new keys."
    exit 1
fi

# 1. Build the Frontend
echo "Building frontend..."
cd frontend

# Install dependencies if node_modules is missing (optional, but good for safety)
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Running build..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

cd ..

# 2. Sync to S3
echo "Deploying to s3://$BUCKET_NAME..."
if [ -d "$DIST_DIR" ]; then
    aws s3 sync $DIST_DIR s3://$BUCKET_NAME --delete
    
    if [ $? -eq 0 ]; then
        echo "----------------------------------------------------------------"
        echo "✅ Deployment complete!"
        echo "Your app should be live at the S3 website URL (configure in AWS Console)."
        echo "----------------------------------------------------------------"
    else
        echo "❌ Upload failed. Please check your AWS permissions and bucket name."
    fi
else
    echo "❌ Build directory '$DIST_DIR' not found. Build process might have failed silently."
    exit 1
fi

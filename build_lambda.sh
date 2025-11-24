#!/bin/bash
set -e # Fail immediately if any command fails

# 1. Create a build directory
rm -rf lambda_build
mkdir -p lambda_build

# 2. Install dependencies into the build directory
echo "Installing dependencies (Linux x86_64 compatible)..."
# We use --platform manylinux2014_x86_64 to ensure we get binaries compatible with AWS Lambda
# We use --only-binary=:all: to force downloading wheels instead of compiling from source
python3 -m pip install \
    --platform manylinux2014_x86_64 \
    --target=lambda_build \
    --implementation cp \
    --python-version 3.13 \
    --only-binary=:all: --upgrade \
    -r backend/requirements-lambda.txt

# 3. Copy application code
echo "Copying application code..."
# We copy the 'backend' directory itself so it acts as a package
# This allows 'backend.main.handler' to work and preserves relative imports
# EXCLUDE virtual environments and other junk!
rsync -av --progress backend lambda_build/ \
    --exclude myenv \
    --exclude venv \
    --exclude .env \
    --exclude .git \
    --exclude __pycache__ \
    --exclude "*.pyc" \
    --exclude ".DS_Store"

# 4. Remove unnecessary files to reduce size
echo "Cleaning up..."
# Remove __pycache__
find lambda_build -name "__pycache__" -type d -exec rm -r {} +
# Remove tests, docs, examples from installed packages
find lambda_build -name "tests" -type d -exec rm -rf {} +
find lambda_build -name "docs" -type d -exec rm -rf {} +
find lambda_build -name "examples" -type d -exec rm -rf {} +
find lambda_build -name "*.dist-info" -type d -exec rm -rf {} +
find lambda_build -name "*.egg-info" -type d -exec rm -rf {} +
# Explicitly remove boto3/botocore if they snuck in (Lambda has them)
rm -rf lambda_build/boto3*
rm -rf lambda_build/botocore*
# Remove uvicorn (not needed for Lambda)
rm -rf lambda_build/uvicorn*

# Verify fastapi exists
if [ ! -d "lambda_build/fastapi" ]; then
    echo "ERROR: fastapi not found in lambda_build!"
    ls -F lambda_build
    exit 1
fi

# Fix permissions (Lambda needs world-readable files)
chmod -R 755 lambda_build

# DEBUG: Show what is taking up space
echo "--- Build Directory Size Breakdown ---"
du -h -d 1 lambda_build | sort -h
echo "--------------------------------------"

# 5. Zip it up
echo "Creating deployment.zip..."
cd lambda_build
zip -q -r ../deployment.zip .
cd ..

# 6. Cleanup
rm -rf lambda_build

echo "Done! Upload 'deployment.zip' to AWS Lambda."
echo "Set Handler to: backend.main.handler"

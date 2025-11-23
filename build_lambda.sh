#!/bin/bash

# 1. Create a build directory
mkdir -p lambda_build

# 2. Install dependencies into the build directory
echo "Installing dependencies (Linux x86_64 compatible)..."
# We use --platform manylinux2014_x86_64 to ensure we get binaries compatible with AWS Lambda
# We use --only-binary=:all: to force downloading wheels instead of compiling from source
pip install \
    --platform manylinux2014_x86_64 \
    --target=lambda_build \
    --implementation cp \
    --python-version 3.13 \
    --only-binary=:all: --upgrade \
    -r backend/requirements.txt

# 3. Copy application code
echo "Copying application code..."
# We copy the 'backend' directory itself so it acts as a package
# This allows 'backend.main.handler' to work and preserves relative imports
cp -r backend lambda_build/

# 4. Remove unnecessary files (pycache, etc.)
find lambda_build -name "__pycache__" -type d -exec rm -r {} +
# find lambda_build -name "*.dist-info" -type d -exec rm -r {} + # KEEP dist-info! Required for modern packages.

# 5. Zip it up
echo "Creating deployment.zip..."
cd lambda_build
zip -r ../deployment.zip .
cd ..

# 6. Cleanup
rm -rf lambda_build

echo "Done! Upload 'deployment.zip' to AWS Lambda."
echo "Set Handler to: backend.main.handler"

#!/bin/bash

BUCKET_NAME="llm-prompt-repo-lambda-code"
ZIP_FILE="deployment.zip"

# 1. Build the zip using the existing script
echo "Building deployment package..."
if [ -f "./build_lambda.sh" ]; then
    ./build_lambda.sh
else
    echo "Error: build_lambda.sh not found!"
    exit 1
fi

# 2. Upload to S3
echo "Uploading $ZIP_FILE to s3://$BUCKET_NAME/..."
aws s3 cp $ZIP_FILE s3://$BUCKET_NAME/$ZIP_FILE

if [ $? -eq 0 ]; then
    echo "----------------------------------------------------------------"
    echo "✅ Upload complete!"
    echo "Go to AWS Lambda Console -> Code -> Upload from -> Amazon S3 Location"
    echo "Paste this URL: s3://$BUCKET_NAME/$ZIP_FILE"
    echo "----------------------------------------------------------------"
else
    echo "❌ Upload failed. Please check your AWS credentials and bucket name."
fi

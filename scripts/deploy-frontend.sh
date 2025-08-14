#!/bin/bash
# Deploy frontend to Google Cloud Storage

echo "🚀 Deploying Agentiqware Frontend..."

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi
cd ..

# Upload to Google Cloud Storage
echo "☁️ Uploading to Google Cloud Storage..."
gcloud storage cp -r frontend/build/* gs://agentiqware-frontend/

# Set proper content types and caching
echo "⚙️ Configuring content types..."
gcloud storage objects update gs://agentiqware-frontend/index.html --content-type='text/html' --cache-control='no-cache'
gcloud storage objects update gs://agentiqware-frontend/static/js/* --content-type='application/javascript' --cache-control='max-age=31536000'
gcloud storage objects update gs://agentiqware-frontend/static/css/* --content-type='text/css' --cache-control='max-age=31536000'

# Verify deployment
echo "🔍 Verifying deployment..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://storage.googleapis.com/agentiqware-frontend/index.html)
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Frontend deployed successfully!"
    echo "🌐 URL: https://storage.googleapis.com/agentiqware-frontend/index.html"
    echo "📱 Title: $(curl -s https://storage.googleapis.com/agentiqware-frontend/index.html | grep -o '<title>[^<]*</title>')"
else
    echo "❌ Deployment verification failed (HTTP $RESPONSE)"
    exit 1
fi
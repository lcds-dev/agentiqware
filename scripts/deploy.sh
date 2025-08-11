#!/bin/bash
# Deploy to production

echo "Deploying Agentiqware to production..."

# Build frontend
cd frontend
npm run build

# Deploy to GCP
gcloud app deploy --project=$GCP_PROJECT_ID

# Deploy Cloud Functions
cd ../backend/functions
for func in */; do
  gcloud functions deploy ${func%/} \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated
done

echo "Deployment complete!"

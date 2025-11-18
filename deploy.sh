#!/bin/bash

# Bushido Game Testing Agent - Deployment Script
# This script prepares and deploys the agent to Google Vertex AI

set -e  # Exit on error

echo "=================================="
echo "Bushido Testing Agent Deployment"
echo "=================================="

# Check for required environment variables
check_env_var() {
    if [ -z "${!1}" ]; then
        echo "Error: $1 is not set"
        echo "Please export $1=<value> before running this script"
        exit 1
    fi
}

# Optional but recommended environment variables
suggest_env_var() {
    if [ -z "${!1}" ]; then
        echo "Warning: $1 is not set (optional but recommended)"
    fi
}

echo ""
echo "Checking environment configuration..."

# Required variables
check_env_var "GOOGLE_CLOUD_PROJECT"

# API Key should be in environment or Secret Manager
if [ -z "$GOOGLE_AI_API_KEY" ]; then
    echo "Warning: GOOGLE_AI_API_KEY not set in environment"
    echo "Will attempt to retrieve from Secret Manager at runtime"
fi

# Optional variables
suggest_env_var "GOOGLE_CLOUD_LOCATION"
suggest_env_var "RESULTS_BUCKET"
suggest_env_var "SERVICE_ACCOUNT"

echo ""
echo "Configuration verified!"

# Set defaults if not provided
export GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}

echo ""
echo "Using configuration:"
echo "  Project: $GOOGLE_CLOUD_PROJECT"
echo "  Location: $GOOGLE_CLOUD_LOCATION"
echo "  Results Bucket: ${RESULTS_BUCKET:-'(will use local storage)'}"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Authenticate with Google Cloud
echo ""
echo "Authenticating with Google Cloud..."
gcloud auth application-default login --project=$GOOGLE_CLOUD_PROJECT

# Enable required APIs
echo ""
echo "Enabling required Google Cloud APIs..."
gcloud services enable aiplatform.googleapis.com \
    secretmanager.googleapis.com \
    storage.googleapis.com \
    --project=$GOOGLE_CLOUD_PROJECT

# Create results bucket if specified and doesn't exist
if [ ! -z "$RESULTS_BUCKET" ]; then
    echo ""
    echo "Creating results bucket if it doesn't exist..."
    gsutil mb -p $GOOGLE_CLOUD_PROJECT -l $GOOGLE_CLOUD_LOCATION gs://$RESULTS_BUCKET || true
    
    # Set bucket lifecycle to clean up old results (optional)
    cat > /tmp/lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 30,
          "matchesPrefix": ["bushido-simulations/"]
        }
      }
    ]
  }
}
EOF
    
    gsutil lifecycle set /tmp/lifecycle.json gs://$RESULTS_BUCKET
    rm /tmp/lifecycle.json
    
    echo "Results bucket configured: gs://$RESULTS_BUCKET"
fi

# Create secret for API key if not in environment
if [ ! -z "$GOOGLE_AI_API_KEY" ]; then
    echo ""
    echo "Storing API key in Secret Manager..."
    echo -n "$GOOGLE_AI_API_KEY" | gcloud secrets create google-ai-api-key \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$GOOGLE_CLOUD_PROJECT || true
    
    echo "API key stored securely in Secret Manager"
fi

# Package the application
echo ""
echo "Packaging application for deployment..."
tar -czf bushido_agent.tar.gz \
    bushido_test_agent.py \
    vertex_ai_config.py \
    requirements.txt

# Upload package to GCS if bucket is specified
if [ ! -z "$RESULTS_BUCKET" ]; then
    echo "Uploading package to GCS..."
    gsutil cp bushido_agent.tar.gz gs://$RESULTS_BUCKET/packages/
    echo "Package uploaded to gs://$RESULTS_BUCKET/packages/bushido_agent.tar.gz"
fi

echo ""
echo "=================================="
echo "Deployment Preparation Complete!"
echo "=================================="
echo ""
echo "To run locally:"
echo "  python bushido_test_agent.py"
echo ""

if [ ! -z "$RESULTS_BUCKET" ]; then
    echo "To deploy to Vertex AI:"
    echo "  python -c \"from vertex_ai_config import deploy_to_vertex_ai; deploy_to_vertex_ai()\""
else
    echo "To deploy to Vertex AI:"
    echo "  1. Set RESULTS_BUCKET environment variable"
    echo "  2. Re-run this script"
    echo "  3. Run: python -c \"from vertex_ai_config import deploy_to_vertex_ai; deploy_to_vertex_ai()\""
fi

echo ""
echo "For production deployment, ensure you:"
echo "  1. Use a service account with minimal required permissions"
echo "  2. Enable VPC-SC if handling sensitive data"
echo "  3. Use Customer-Managed Encryption Keys (CMEK) if required"
echo "  4. Set up monitoring and alerting"
echo ""
echo "Done!"

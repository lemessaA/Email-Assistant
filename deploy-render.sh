#!/bin/bash

# Email Assistant Render Deployment Script

echo "🚀 Deploying Email Assistant to Render.com..."

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI not found. Please install it first:"
    echo "npm install -g @render/cli"
    exit 1
fi

# Login to Render
echo "🔐 Logging into Render..."
render login

# Create API service
echo "📡 Creating API service..."
render create web-service \
  --name email-assistant-api \
  --runtime python \
  --region oregon \
  --plan free \
  --build-command "pip install -r requirements.txt" \
  --start-command "uvicorn src.api.main:app --host 0.0.0.0 --port \$PORT" \
  --health-check-path /health

# Create UI service
echo "🎨 Creating UI service..."
render create web-service \
  --name email-assistant-ui \
  --runtime python \
  --region oregon \
  --plan free \
  --build-command "pip install -r requirements.txt" \
  --start-command "streamlit run src/ui/streamlit_app.py --server.port \$PORT --server.address 0.0.0.0" \
  --health-check-path /

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your services:"
echo "  API: https://email-assistant-api.onrender.com"
echo "  UI: https://email-assistant-ui.onrender.com"
echo ""
echo "🔧 Don't forget to set environment variables in Render dashboard!"

#!/bin/bash
# Streamlit Cloud deployment script

echo "🚀 Deploying KenyaVault Stream Balancer to Production..."

# Install dependencies
pip install -r requirements.txt

# Run in production mode
streamlit run app.py --server.headless true --server.enableCORS false --server.enableXsrfProtection true

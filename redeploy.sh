#!/bin/bash

# Antigravity Agent - Redeploy Script
# Automates the process of pulling latest changes and restarting Streamlit

echo "🚀 Starting Redeploy Process..."

# 1. Navigate to project root
cd ~/stock-trading || { echo "❌ Failed to change directory to ~/stock-trading"; exit 1; }

# 2. Pull latest changes from Git
echo "[*] Pulling latest changes..."
git pull

# 3. Kill existing streamlit processes
echo "[*] Stopping existing streamlit instances..."
pkill -f streamlit || echo "⚠️ No running streamlit process found."

# 4. Run the application in background using nohup
echo "[*] Restarting Streamlit in background..."
nohup ./run.sh > streamlit.log 2>&1 &

echo "✅ Redeploy Complete! Check streamlit.log for details."

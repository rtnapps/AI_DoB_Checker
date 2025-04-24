#!/bin/bash

# Step 1: Install system dependencies
apt-get update
apt-get install -y libgl1 libglib2.0-0

# Step 2: Prepare persistent EasyOCR cache directory
PERSISTENT_CACHE_DIR="/home/.EasyOCR"
APP_CACHE_DIR="/home/site/wwwroot/.EasyOCR"

echo "🔁 Ensuring EasyOCR cache exists at $PERSISTENT_CACHE_DIR"
mkdir -p "$PERSISTENT_CACHE_DIR"

# Step 3: Copy EasyOCR models from app dir if any exist (first-time deploy)
if [ -d "$APP_CACHE_DIR" ]; then
    echo "🗂 Copying EasyOCR models from app to persistent cache"
    cp -r $APP_CACHE_DIR/* $PERSISTENT_CACHE_DIR/ || true
else
    echo "⚠️ No EasyOCR cache found in $APP_CACHE_DIR"
fi

# Step 4: Start the Flask app via gunicorn
echo "🚀 Starting Gunicorn server..."
gunicorn -w 4 -b 0.0.0.0:8000 app:app

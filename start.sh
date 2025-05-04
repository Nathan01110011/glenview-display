#!/bin/bash

cd /home/nathan/Documents/Repositories/glenview-display
source .venv/bin/activate

DEVICE_ID="${DEVICE_ID:-frame1}"
CONFIG_FILE="/home/nathan/Documents/Repositories/glenview-display/display-app/dog_config/${DEVICE_ID}.toml"
IS_SERVER=$(grep -E '^IS_SERVER\s*=' "$CONFIG_FILE" | awk -F= '{print $2}' | tr -d ' "')

if [ "$IS_SERVER" = "true" ]; then
    echo "🚀 Starting backend server..."
    cd backend
    exec uvicorn rest_server:app --host 0.0.0.0 --port 8000
else
    echo "🖥️ Launching display app..."
    cd display-app
    exec python main.py
fi
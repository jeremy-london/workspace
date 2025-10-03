#!/bin/bash
set -e

# Check if models need to be downloaded (check for marker file in cache volume)
MODEL_CACHE_MARKER="/root/.cache/huggingface/.models_downloaded"

if [ ! -f "$MODEL_CACHE_MARKER" ]; then
    echo "🚀 First run detected - downloading embedding models..."
    python /usr/local/bin/preload_models.py
    
    # Create marker file to skip this on subsequent runs
    touch "$MODEL_CACHE_MARKER"
else
    echo "✅ Models already cached, skipping download"
fi

# Execute the main command
exec "$@"
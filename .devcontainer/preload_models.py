#!/usr/bin/env python3
"""
Pre-download embedding models for faster container startup.
This script downloads all the models used by the application to avoid
runtime delays when they're first accessed.
"""

import os
import sys
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Models to pre-download based on the model_map in ingest_knowledge_interactive.py
MODELS_TO_DOWNLOAD = [
    "BAAI/bge-base-en-v1.5",
    "BAAI/bge-large-en-v1.5", 
    "intfloat/e5-large-v2"
]

def is_model_cached(model_name: str) -> bool:
    """Check if model is already cached locally."""
    try:
        # Try to load the model without downloading
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        model_path = cache_dir / f"models--{model_name.replace('/', '--')}"
        
        if model_path.exists() and any(model_path.iterdir()):
            # Check if it has the necessary files
            snapshots_dir = model_path / "snapshots"
            if snapshots_dir.exists() and any(snapshots_dir.iterdir()):
                return True
        return False
    except Exception:
        return False

def download_model(model_name: str) -> bool:
    """Download a single model with progress indication."""
    try:
        # Check if model is already cached
        if is_model_cached(model_name):
            print(f"⚡ {model_name} already cached, skipping download")
            return True
        
        print(f"📥 Downloading {model_name}...")
        
        # Initialize progress bar
        pbar = tqdm(
            total=100, 
            desc=f"  {model_name.split('/')[-1]}", 
            unit="%",
            leave=True
        )
        
        # Download the model
        model = SentenceTransformer(model_name)
        
        # Complete the progress bar
        pbar.n = 100
        pbar.refresh()
        pbar.close()
        
        print(f"✅ Successfully downloaded {model_name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {model_name}: {e}")
        return False

def main():
    """Main function to download all models."""
    print("🚀 Starting model pre-download process...")
    print(f"📋 Models to download: {len(MODELS_TO_DOWNLOAD)}")
    print()
    
    successful_downloads = 0
    failed_downloads = 0
    
    for model_name in MODELS_TO_DOWNLOAD:
        if download_model(model_name):
            successful_downloads += 1
        else:
            failed_downloads += 1
        print()  # Add spacing between models
    
    # Summary
    print("=" * 50)
    print("📊 Download Summary:")
    print(f"✅ Successful: {successful_downloads}")
    print(f"❌ Failed: {failed_downloads}")
    print(f"📦 Total: {len(MODELS_TO_DOWNLOAD)}")
    
    if failed_downloads > 0:
        print("\n⚠️  Some models failed to download. Check the errors above.")
        sys.exit(1)
    else:
        print("\n🎉 All models downloaded successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()

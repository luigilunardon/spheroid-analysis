#!/bin/bash
# Clean build artifacts

echo "Cleaning build artifacts..."

# Remove build directory
if [ -d "build" ]; then
    echo "Removing build/"
    rm -rf build/
fi

# Remove dist contents except zips
if [ -d "dist" ]; then
    echo "Cleaning dist/ (keeping .zip files)"
    find dist/ -type f ! -name "*.zip" -delete
    find dist/ -type d -mindepth 1 -delete
fi

# Remove Python cache
echo "Removing __pycache__/"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
find . -type f -name "*.pyc" -delete

echo "✓ Clean complete!"

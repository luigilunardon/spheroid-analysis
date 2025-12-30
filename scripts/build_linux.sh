#!/bin/bash
# Build Linux executable

echo "Building Spheroid Analysis for Linux..."

# Activate virtual environment
source .venv/bin/activate

# Build with PyInstaller
pyinstaller --name="SpheroidAnalysis" \
    --windowed \
    --onefile \
    --add-data="app_logo.png:." \
    --add-data="app_icon.png:." \
    --hidden-import=PIL._tkinter_finder \
    spheroid_app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
    echo ""
    echo "Executable created at: dist/SpheroidAnalysis"
    echo ""
    echo "To make executable: chmod +x dist/SpheroidAnalysis"
    echo "To run: ./dist/SpheroidAnalysis"
    echo "To distribute: Share dist/SpheroidAnalysis"
else
    echo "✗ Build failed!"
    exit 1
fi

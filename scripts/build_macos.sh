#!/bin/bash
# Build macOS application bundle

echo "Building Spheroid Analysis for macOS..."

# Activate virtual environment
source .venv/bin/activate

# Build with PyInstaller
pyinstaller spheroid_app.spec --clean --noconfirm

if [ $? -eq 0 ]; then
    echo "✓ Build successful!"
    echo ""
    echo "Application created at: dist/SpheroidAnalysis.app"
    
    # Create ZIP archive
    cd dist
    if [ -d "SpheroidAnalysis.app" ]; then
        zip -r SpheroidAnalysis-macOS.zip SpheroidAnalysis.app
        echo "✓ Created ZIP: dist/SpheroidAnalysis-macOS.zip"
    fi
    cd ..
    
    echo ""
    echo "To test: open dist/SpheroidAnalysis.app"
    echo "To distribute: Use dist/SpheroidAnalysis-macOS.zip"
else
    echo "✗ Build failed!"
    exit 1
fi

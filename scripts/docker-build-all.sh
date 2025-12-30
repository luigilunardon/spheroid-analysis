#!/bin/bash
# Build script using Docker for all platforms

set -e

echo "Building Spheroid Analysis for all platforms..."
echo "============================================================"

# Create dist directory
mkdir -p dist

# Build for macOS (native, not Docker)
echo ""
echo "Building for macOS..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    ./scripts/build_macos.sh
    # Create ZIP archive
    cd dist
    if [ -d "SpheroidAnalysis.app" ]; then
        zip -r SpheroidAnalysis-macOS.zip SpheroidAnalysis.app
        echo "✓ Created SpheroidAnalysis-macOS.zip"
    fi
    cd ..
else
    echo "⚠ Skipping macOS build (not running on macOS)"
fi

# Build for Debian-based Linux (x86_64)
echo ""
echo "Building for Debian Linux (x86_64)..."
docker build --platform linux/amd64 -f .devcontainer/debian.Dockerfile -t spheroid-build-debian .
docker run --rm --platform linux/amd64 -v "$(pwd)/dist:/workspace/dist" spheroid-build-debian
# Create ZIP archive
cd dist
if [ -f "SpheroidAnalysis" ]; then
    zip SpheroidAnalysis-Linux-Debian.zip SpheroidAnalysis
    echo "✓ Created SpheroidAnalysis-Linux-Debian.zip"
fi
cd ..

# Build for RedHat-based Linux (x86_64)
echo ""
echo "Building for RedHat Linux (x86_64)..."
docker build --platform linux/amd64 -f .devcontainer/redhat.Dockerfile -t spheroid-build-redhat .
docker run --rm --platform linux/amd64 -v "$(pwd)/dist:/workspace/dist" spheroid-build-redhat
mv dist/SpheroidAnalysis dist/SpheroidAnalysis-redhat
# Create ZIP archive
cd dist
if [ -f "SpheroidAnalysis-redhat" ]; then
    zip SpheroidAnalysis-Linux-RedHat.zip SpheroidAnalysis-redhat
    echo "✓ Created SpheroidAnalysis-Linux-RedHat.zip"
fi
cd ..

# Build for Windows (using Wine, x86_64)
echo ""
echo "Building for Windows (x86_64)..."
docker build --platform linux/amd64 -f .devcontainer/windows.Dockerfile -t spheroid-build-windows .
docker run --rm --platform linux/amd64 -v "$(pwd)/dist:/workspace/dist" spheroid-build-windows
# Create ZIP archive
cd dist
if [ -f "SpheroidAnalysis.exe" ]; then
    zip SpheroidAnalysis-Windows.zip SpheroidAnalysis.exe
    echo "✓ Created SpheroidAnalysis-Windows.zip"
fi
cd ..

echo ""
echo "============================================================"
echo "✓ All builds complete!"
echo "Output files in dist/:"
ls -lh dist/

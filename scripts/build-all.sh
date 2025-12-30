#!/bin/bash
# Build script for all platforms (native macOS, Docker for cross-platform Linux)

set -e

echo "Building Spheroid Analysis for all platforms..."
echo "============================================================"

# Create dist directory
mkdir -p dist

# Build for macOS (native build)
echo ""
echo "Building for macOS..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    ./scripts/build_macos.sh
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
mv dist/SpheroidAnalysis dist/SpheroidAnalysis-redhat 2>/dev/null || true
# Create ZIP archive
cd dist
if [ -f "SpheroidAnalysis-redhat" ]; then
    zip SpheroidAnalysis-Linux-RedHat.zip SpheroidAnalysis-redhat
    echo "✓ Created SpheroidAnalysis-Linux-RedHat.zip"
fi
cd ..

echo ""
echo "============================================================"
echo "✓ All builds complete!"
echo ""
echo "Note: Windows builds must be created on a Windows machine using:"
echo "  scripts/build_windows.bat"
echo ""
echo "Output files in dist/:"
ls -lh dist/

# Clean build artifacts (keep .zip files)
echo ""
echo "Cleaning build artifacts..."
./scripts/clean.sh

# Cross-Platform Build with Docker

This directory contains Docker configurations for building the Spheroid Analysis application on Windows, Debian Linux, and RedHat Linux without needing access to those platforms.

## Quick Start

Build for all platforms:
```bash
./scripts/docker-build-all.sh
```

The built executables will be in `dist/`:
- `SpheroidAnalysis.exe` - Windows executable
- `SpheroidAnalysis` - Debian Linux executable
- `SpheroidAnalysis-redhat` - RedHat/AlmaLinux executable

## Individual Builds

### Debian Linux
```bash
docker build -f .devcontainer/debian.Dockerfile -t spheroid-build-debian .
docker run --rm -v "$(pwd)/dist:/workspace/dist" spheroid-build-debian
```

### RedHat/AlmaLinux
```bash
docker build -f .devcontainer/redhat.Dockerfile -t spheroid-build-redhat .
docker run --rm -v "$(pwd)/dist:/workspace/dist" spheroid-build-redhat
```

### Windows (via Wine)
```bash
docker build -f .devcontainer/windows.Dockerfile -t spheroid-build-windows .
docker run --rm -v "$(pwd)/dist:/workspace/dist" spheroid-build-windows
```

## Requirements

- Docker installed and running
- ~2GB disk space for images
- ~1GB disk space for builds

## Troubleshooting

**Build fails with permission errors:**
```bash
chmod +x scripts/*.sh
```

**Docker out of space:**
```bash
docker system prune -a
```

**Windows build very slow:**
Wine emulation is slow. The Windows build may take 10-15 minutes. Consider building natively on Windows for faster results.

## Notes

- Wine-based Windows builds are functional but may have minor issues
- For production releases, prefer native Windows builds
- Linux builds are fully native and fast
- Each Dockerfile installs dependencies from scratch for reproducibility

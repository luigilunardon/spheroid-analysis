# macOS build container (for cross-compilation from Linux/other platforms)
# Note: This uses OSXCross for cross-compilation - complex setup required

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install base dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    python3-venv \
    wget \
    git \
    cmake \
    libssl-dev \
    libxml2-dev \
    libz-dev \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Note: Full macOS cross-compilation setup is complex and requires:
# 1. OSXCross toolchain
# 2. macOS SDK (requires Apple Developer account)
# 3. Special PyInstaller configuration for cross-platform builds
#
# For actual macOS builds, it's recommended to use a native macOS machine
# or GitHub Actions with macos-latest runner.
#
# This Dockerfile serves as a template but requires additional setup.

WORKDIR /workspace

# Copy project files
COPY pyproject.toml /workspace/
COPY src/ /workspace/src/
COPY scripts/ /workspace/scripts/
COPY spheroid_app.spec /workspace/

# Install Python dependencies
RUN python3.12 -m pip install .

# Build script would go here, but requires OSXCross setup
# For now, this serves as documentation

CMD ["/bin/bash", "-c", "echo 'macOS cross-compilation requires OSXCross setup. Use native macOS or GitHub Actions instead.'"]

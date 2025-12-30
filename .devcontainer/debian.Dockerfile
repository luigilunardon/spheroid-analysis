# Debian-based Linux build container
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    python3-venv \
    libgtk-3-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install Python dependencies
COPY pyproject.toml /workspace/
RUN python3.12 -m pip install --break-system-packages .

# Build script
COPY scripts/build_linux.sh /build_linux.sh
RUN chmod +x /build_linux.sh

CMD ["/bin/bash", "/build_linux.sh"]

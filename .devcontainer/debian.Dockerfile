# Debian-based Linux build container
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libgtk-3-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy project files
COPY pyproject.toml README.md /workspace/
COPY src/ /workspace/src/

# Install Python dependencies
RUN python3 -m pip install --break-system-packages .

# Copy spec file
COPY spheroid_app.spec /workspace/

CMD ["pyinstaller", "--clean", "--noconfirm", "spheroid_app.spec"]

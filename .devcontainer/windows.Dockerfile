# Windows build container using Wine
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Wine and dependencies
RUN apt-get update && apt-get install -y \
    wine64 \
    wine32 \
    python3.12 \
    python3-pip \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python for Windows via Wine
RUN wget https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe -O /tmp/python-installer.exe \
    && wine64 /tmp/python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 \
    && rm /tmp/python-installer.exe

WORKDIR /workspace

# Copy and install dependencies
COPY pyproject.toml /workspace/
RUN wine64 python -m pip install .

# Build script
COPY scripts/build_windows.bat /build_windows.bat
RUN chmod +x /build_windows.bat

CMD ["/bin/bash", "-c", "wine64 cmd /c build_windows.bat && cp -r dist/* /workspace/dist/"]

# RedHat-based Linux build container
FROM almalinux:9

# Install Python and dependencies
RUN dnf install -y \
    python3.12 \
    python3-pip \
    gtk3 \
    libSM \
    libXext \
    libXrender \
    && dnf clean all

WORKDIR /workspace

# Install Python dependencies
COPY pyproject.toml /workspace/
RUN python3.12 -m pip install .

# Build script
COPY scripts/build_linux.sh /build_linux.sh
RUN chmod +x /build_linux.sh

CMD ["/bin/bash", "/build_linux.sh"]

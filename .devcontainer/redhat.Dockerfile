# RedHat-based Linux build container
FROM almalinux:9

# Install Python and dependencies
RUN dnf install -y \
    python3.12 \
    python3.12-pip \
    gtk3 \
    libSM \
    libXext \
    libXrender \
    && dnf clean all

WORKDIR /workspace

# Copy project files
COPY pyproject.toml README.md /workspace/
COPY src/ /workspace/src/

# Install Python dependencies
RUN python3.12 -m pip install .

# Copy spec file
COPY spheroid_app.spec /workspace/

CMD ["pyinstaller", "--clean", "--noconfirm", "spheroid_app.spec"]

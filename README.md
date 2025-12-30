# Spheroid Analysis

User-friendly application for analyzing spheroid images to identify core, border, and background regions.

---

## For Users

### Download

Download the latest release for your platform from the [Releases](https://github.com/luigilunardon/spheroid-analysis/releases) page:

- **macOS**: `SpheroidAnalysis-macOS.zip`
- **Windows**: `SpheroidAnalysis-Windows.zip`
- **Linux (Debian/Ubuntu)**: `SpheroidAnalysis-Linux-Debian.zip`
- **Linux (RedHat/Fedora/AlmaLinux)**: `SpheroidAnalysis-Linux-RedHat.zip`

### Installation & First Launch

**macOS:**
1. Download `SpheroidAnalysis-macOS.zip`
2. Unzip the file and drag `SpheroidAnalysis.app` to the Applications folder
3. Right-click the app and select "Open" (required for unsigned apps)
4. Click "Open" in the security dialog
5. **Note:** The app is not code-signed, so macOS will show a security warning on first launch

**Windows:**
1. Download `SpheroidAnalysis-Windows.zip`
2. Extract the ZIP file
3. Double-click `SpheroidAnalysis.exe` to run
4. If Windows Defender blocks: Click "More info" → "Run anyway"

**Linux:**
1. Download the appropriate ZIP for your distribution
2. Extract: `unzip SpheroidAnalysis-Linux-*.zip`
3. Make executable: `chmod +x SpheroidAnalysis`
4. Run: `./SpheroidAnalysis`

### Quick Start

1. Click **"Load Image"** - select your spheroid image
2. Adjust sliders to fine-tune detection (hover **i** buttons for help) and crop the image
3. Switch between **Overlay** and **Binary** views
4. Click **"Save Results"** to export

### Key Parameters

These sliders help you fine-tune how the software identifies your spheroid and its core region. Hover over the **i** buttons in the app for quick reminders.

| Parameter | Range | What it does | When to adjust | Default |
|-----------|-------|--------------|----------------|---------|
| **Denoise Strength** | 1-20 | Smooths out grainy/noisy images | Increase if your image looks speckled or has noise from the microscope | 10 |
| **Contrast Enhancement** | 1-10 | Makes light and dark areas more distinct | Increase if your spheroid is hard to see or looks washed out | 2.0 |
| **Threshold** | 0-255 | Decides what counts as "spheroid" vs "background" | Adjust if the spheroid outline isn't capturing the right area - lower includes more, higher includes less | 127 |
| **Core Size** | 1-99% | Determines how much of the spheroid is considered "core" (darker region) vs "border" (lighter region) | Set based on your biological definition - 50% splits evenly, lower values give smaller core, higher gives larger core | 50% |
| **Min Area** | pixels | Ignores small specks and artifacts | Increase if small dots are being counted as spheroid pieces | 100 |

**Understanding Core Size:**
The "core" is the darker, denser part of your spheroid. The Core Size percentage tells the software what portion of the spheroid should be classified as core:
- **50%** = The darkest half of the spheroid pixels become the core
- **25%** = Only the darkest quarter is core (if you have a small, dense core)
- **75%** = Most of the spheroid is core (if your core is large or diffuse)

### Understanding Results

- **Red outline:** Spheroid outer edge (border)
- **Yellow outline:** Core boundary
- **Binary view:** White spheroid on black background
- **Pixel counts:** Core, Border, and Total area

---

## For Developers

### Setup

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
# Clone the repository
git clone https://github.com/luigilunardon/spheroid-analysis.git
cd spheroid-analysis

# Create and activate virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### Run from Source

```bash
python src/spheroid_app.py
```

### Build Executables

**Build macOS and Linux:**
```bash
./scripts/build-all.sh
```

This creates:
- `dist/SpheroidAnalysis-macOS.zip` (native macOS build)
- `dist/SpheroidAnalysis-Linux-Debian.zip` (Docker)
- `dist/SpheroidAnalysis-Linux-RedHat.zip` (Docker)

**Build Windows:**

Windows builds must be created on a Windows machine:
```cmd
scripts\build_windows.bat
```

This creates `dist/SpheroidAnalysis.exe`

**Requirements:**
- macOS build: Must run on macOS with `uv` installed
- Linux builds: Require Docker (can run on any OS)
- Windows build: Must run on Windows with `uv` installed

**Version 1.0.0** | December 2025
License: MIT
# Spheroid Analysis

User-friendly application for analyzing spheroid images to identify core, border, and background regions.

---

## For Users

### Installation & First Launch

**macOS:**
1. Download `SpheroidAnalysis-macOS.zip`
2. Unzip and drag `SpheroidAnalysis.app` to Applications
3. **Double-click to launch**
4. **First launch note:** App may require 2-3 clicks to start (normal for unsigned apps - this only happens once)
5. If security warning appears: Right-click → Open → Open

**Windows:**
1. Download `SpheroidAnalysis.exe`
2. Double-click to run
3. If Windows Defender blocks: Click "More info" → "Run anyway"

**Linux:**
1. Download `SpheroidAnalysis`
2. Make executable: `chmod +x SpheroidAnalysis`
3. Run: `./SpheroidAnalysis`

### Quick Start

1. Click **"Load Image"** - select your spheroid image
2. Adjust sliders to fine-tune detection (hover **?** buttons for help)
3. Switch between **Overlay** and **Binary** views
4. Click **"Save Results"** to export

### Key Parameters

| Parameter | Range | Description | Default |
|-----------|-------|-------------|---------|
| Denoise Strength | 1-20 | Remove noise (decimal) | 10 |
| Contrast Enhancement | 1-10 | Improve visibility (decimal) | 2.0 |
| Threshold | 0-255 | Separate spheroid from background | 127 |
| **Core Size** | 1-99% | **Higher = larger core region** | 50% |
| Min Area | pixels | Filter noise | 100 |

**Core Size explained:**
- Identifies the darkest pixels within the spheroid as "core"
- **50%** = Half the spheroid is core (median split)
- **25%** = Only darkest quarter is core (small core)
- **75%** = Three-quarters is core (large core)

### Understanding Results

- **Red outline:** Spheroid outer edge (border)
- **Yellow outline:** Core boundary
- **Binary view:** White spheroid on black background
- **Pixel counts:** Core, Border, and Total area

---

## For Developers

### Setup

```bash
git clone <repo-url>
cd pycvballs
uv venv && source .venv/bin/activate
uv pip install -e .
```

### Run from Source

```bash
python src/spheroid_app.py
```

### Build Executables

| Platform | Command | Output |
|----------|---------|--------|
| macOS | `./scripts/build_macos.sh` | `dist/SpheroidAnalysis.app` |
| Windows | `scripts/build_windows.bat` | `dist/SpheroidAnalysis.exe` |
| Linux | `./scripts/build_linux.sh` | `dist/SpheroidAnalysis` |

**Package macOS app:**
```bash
cd dist
ditto -c -k --sequesterRsrc --keepParent SpheroidAnalysis.app SpheroidAnalysis-macOS.zip
```

### Project Structure

```
├── src/
│   ├── spheroid_app.py          # GUI application
│   ├── spheroid_processor.py    # Image processing core
│   └── app_logo.png             # App icon
├── scripts/
│   ├── build_macos.sh           # macOS build script
│   ├── build_windows.bat        # Windows build script
│   ├── build_linux.sh           # Linux build script
│   └── clean.sh                 # Clean build artifacts
├── pyproject.toml               # Project config & dependencies
├── requirements.txt             # Legacy pip requirements
└── spheroid_app.spec            # PyInstaller configuration
├── build_windows.bat        # Windows build script
└── build_linux.sh           # Linux build script
```

### Dependencies

- Python 3.12
- opencv-python 4.11.0
- numpy 2.4.0
- Pillow 12.0.0
- customtkinter 5.2.2
- pyinstaller 6.17.0

### Troubleshooting

**macOS: App requires multiple clicks on first launch**
- Normal for unsigned apps
- Only happens once
- To fix permanently: code sign with Apple Developer ID ($99/year)

**Build fails:**
- Use Python 3.12 (not 3.13)
- macOS: `xcode-select --install`
- Linux: `sudo apt-get install python3-tk build-essential`
- Windows: Use Command Prompt, not PowerShell

**Security warnings:**
- macOS: Right-click → Open
- Windows: "More info" → "Run anyway"
- For production: use code signing

---

## Technical Details

### Image Processing Pipeline

1. **Denoise:** Non-local Means Denoising
2. **Normalize:** Stretch to 0-255 range
3. **Enhance:** CLAHE (local) or global contrast
4. **Auto-invert:** Detect dark-on-light images
5. **Threshold:** Binary segmentation
6. **Morphology:** Noise cleanup
7. **Core detection:** Intensity-based classification

### Core Detection Algorithm

After inversion (spheroid = white on black):
- **Core pixels:** BRIGHTER than (100 - percentile) threshold
- Originally darker pixels → brighter after inversion → core
- **Border pixels:** Remaining spheroid area
- **Higher percentile** → larger core region

Example with 50% percentile:
- Darkest 50% of original spheroid pixels → core
- Lightest 50% → border

### Performance

- ~1 second for 1000×1000 images
- ~5-10 seconds for 4000×4000 images
- Memory: ~200-500 MB
- App size: ~55 MB

---

**Version 1.0.0** | December 2025

License: [Add your license]
Contact: [Add your contact info]

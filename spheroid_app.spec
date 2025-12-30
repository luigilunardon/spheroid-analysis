# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/spheroid_app.py'],
    pathex=[],
    binaries=[],
    datas=[('src/app_logo.png', '.'), ('src/app_icon.png', '.')],
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SpheroidAnalysis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# For macOS app bundle
app = BUNDLE(
    exe,
    name='SpheroidAnalysis.app',
    icon='src/app_logo.png',
    bundle_identifier='com.spheroidanalysis.app',
    info_plist={
        'CFBundleName': 'Spheroid Analysis',
        'CFBundleDisplayName': 'Spheroid Analysis',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
    },
)

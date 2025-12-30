@echo off
REM Build Windows executable

echo Building Spheroid Analysis for Windows...

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Build with PyInstaller
pyinstaller --name="SpheroidAnalysis" ^
    --windowed ^
    --onefile ^
    --add-data="app_logo.png;." ^
    --hidden-import=PIL._tkinter_finder ^
    spheroid_app.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo.
    echo Executable created at: dist\SpheroidAnalysis.exe
    
    REM Create ZIP archive
    cd dist
    if exist SpheroidAnalysis.exe (
        powershell Compress-Archive -Path SpheroidAnalysis.exe -DestinationPath SpheroidAnalysis-Windows.zip -Force
        echo Created ZIP: dist\SpheroidAnalysis-Windows.zip
    )
    cd ..
    
    echo.
    echo To distribute: Use dist\SpheroidAnalysis-Windows.zip
    
    REM Clean build artifacts (keep .zip files)
    echo.
    echo Cleaning build artifacts...
    if exist build rmdir /s /q build
    if exist dist\SpheroidAnalysis.exe del /q dist\SpheroidAnalysis.exe
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
    del /s /q *.pyc 2>nul
    echo Clean complete!
) else (
    echo.
    echo Build failed!
    exit /b 1
)

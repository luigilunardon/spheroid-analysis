@echo off
REM Build Windows executable

echo Building Spheroid Analysis for Windows...

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Build with PyInstaller
pyinstaller --name="SpheroidAnalysis" ^
    --windowed ^
    --onefile ^
    --icon=app_icon.png ^
    --add-data="app_logo.png;." ^
    --add-data="app_icon.png;." ^
    --hidden-import=PIL._tkinter_finder ^
    spheroid_app.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo.
    echo Executable created at: dist\SpheroidAnalysis.exe
    echo.
    echo To distribute: Share dist\SpheroidAnalysis.exe
) else (
    echo.
    echo Build failed!
    exit /b 1
)

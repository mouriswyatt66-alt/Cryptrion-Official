@echo off
cd /d "%~dp0"
echo.
echo  =========================================
echo   Cryptrion-Official  ^|  by Wyatt Mouris
echo   Building EXE...
echo  =========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Python not found. Install Python 3.11+ from python.org
    pause
    exit /b 1
)

echo  [1/3] Installing packages...
python -m pip install requests psutil pyinstaller --quiet
if %errorlevel% neq 0 (
    echo  ERROR: pip install failed.
    pause
    exit /b 1
)

echo  [2/3] Cleaning old build...
if exist dist   rmdir /s /q dist
if exist build  rmdir /s /q build

echo  [3/3] Building Cryptrion.exe...
python -m PyInstaller Cryptrion.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo  ERROR: Build failed. Check output above.
    pause
    exit /b 1
)

echo.
echo ======================================
echo  BUILD COMPLETE
echo  Output: dist\Cryptrion.exe
echo.
echo  Next steps:
echo  1. Test dist\Cryptrion.exe
echo  2. Create a GitHub Release tagged v1.0.0
echo  3. Upload dist\Cryptrion.exe to the release
echo  4. All users auto-update on next launch
echo ======================================
pause

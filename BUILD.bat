@echo off
echo ======================================
echo  Cryptrion-Official  ^|  by Wyatt Mouris
echo  Building EXE...
echo ======================================
echo.

echo [1/3] Installing Python packages...
pip install -r requirements.txt
if errorlevel 1 ( echo ERROR: pip failed & pause & exit /b 1 )

echo.
echo [2/3] Cleaning old build...
if exist dist   rmdir /s /q dist
if exist build  rmdir /s /q build

echo.
echo [3/3] Building Cryptrion.exe...
pyinstaller Cryptrion.spec --clean
if errorlevel 1 ( echo ERROR: build failed & pause & exit /b 1 )

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

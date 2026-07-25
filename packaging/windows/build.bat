@echo off
REM Build PlaylistForge for Windows with PyInstaller + Inno Setup
REM Run from the project root: packaging\windows\build.bat

setlocal enabledelayedexpansion

set APP=PlaylistForge
set VERSION=0.1.0
set ROOT=%~dp0..\..

echo === Build %APP% v%VERSION% for Windows ===

echo.
echo Step 1: Install dependencies
python -m pip install -e "%ROOT%[dev]"
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

echo.
echo Step 2: PyInstaller build
pyinstaller "%ROOT%\packaging\pyinstaller\playlistforge.windows.spec" --clean --noconfirm
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

echo.
echo Step 3: Create installer with Inno Setup
iscc "%ROOT%\packaging\windows\playlistforge.iss"
if %ERRORLEVEL% neq 0 (
    echo Warning: Inno Setup (iscc) not found or failed.
    echo PyInstaller output is at: %ROOT%\dist\PlaylistForge\
    echo Run iscc manually: iscc "%ROOT%\packaging\windows\playlistforge.iss"
)

echo.
echo === Done ===
if exist "%ROOT%\dist\PlaylistForge-Setup-%VERSION%.exe" (
    echo Installer: %ROOT%\dist\PlaylistForge-Setup-%VERSION%.exe
) else (
    echo Portable:  %ROOT%\dist\PlaylistForge\
)

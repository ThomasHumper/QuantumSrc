@echo off
setlocal

set "ASSET_URL=https://example.com/game-assets/latest.zip"
set "ASSET_DIR=assets"
set "TEMP_ZIP=%TEMP%\game-assets.zip"

echo ========================================
echo       Game Engine Asset Fetcher
echo ========================================
echo.

if not exist "%ASSET_DIR%" (
    echo Creating assets directory...
    mkdir "%ASSET_DIR%"
)

echo Downloading latest assets...
curl -L --fail --progress-bar "%ASSET_URL%" -o "%TEMP_ZIP%"

if errorlevel 1 (
    echo.
    echo ERROR: Asset download failed.
    exit /b 1
)

echo.
echo Extracting assets...

tar -xf "%TEMP_ZIP%" -C "%ASSET_DIR%"

if errorlevel 1 (
    echo.
    echo ERROR: Asset extraction failed.
    del "%TEMP_ZIP%" >nul 2>&1
    exit /b 1
)

del "%TEMP_ZIP%" >nul 2>&1

echo.
echo Assets updated successfully.
echo.

endlocal
exit /b 0

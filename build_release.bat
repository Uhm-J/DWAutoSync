@echo off
setlocal enabledelayedexpansion

echo Building DWAutoSync release package...

rem Set variables
set BUILD_DIR=build
set DIST_DIR=%BUILD_DIR%\DWAutoSync
set README_FILE=%BUILD_DIR%\README.txt
set VERSION_PY=client\version.py
set ZIP_NAME=DWAutoSync.zip

rem Extract version from version.py
echo Extracting version from version.py...
for /f "tokens=3 delims= " %%a in ('findstr "VERSION" %VERSION_PY%') do (
    set VERSION_WITH_QUOTES=%%a
    rem Remove quotes from version string
    set VERSION=!VERSION_WITH_QUOTES:"=!
)

echo Using version: %VERSION%

rem Step 1: Remove existing executable if it exists
echo Removing existing executable...
if exist "%DIST_DIR%\DWAutoSync.exe" (
    del /q "%DIST_DIR%\DWAutoSync.exe"
)

rem Step 2: Run the build script
echo Building executable...
cd client
py .\build.py
cd ..

rem Step 3: Create build directory structure if it doesn't exist
if not exist "%DIST_DIR%" (
    mkdir "%DIST_DIR%"
)

rem Step 4: Move the executable to the build directory
echo Moving executable to build directory...
if exist "DWAutoSync.exe" (
    move "DWAutoSync.exe" "%DIST_DIR%\DWAutoSync.exe"
) else (
    echo ERROR: Built executable not found!
    exit /b 1
)

rem Step 5: Copy icon file if it's not already there
if not exist "%DIST_DIR%\icon.ico" (
    copy "client\icon.ico" "%DIST_DIR%\icon.ico"
)

rem Step 6: Update README.txt with version info
echo Updating README with version information...

rem Create a temporary README with version number
type "%README_FILE%" > temp_readme.txt
echo # Dragon Wilds Auto-Sync v%VERSION% > "%README_FILE%"
for /f "skip=1 delims=" %%i in (temp_readme.txt) do echo %%i >> "%README_FILE%"
del temp_readme.txt

rem Step 7: Create zip file using 7-Zip if available, otherwise prompt for manual zip
echo Creating release zip file...
if exist "%ZIP_NAME%" (
    del /q "%ZIP_NAME%"
)

where 7z >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    7z a -tzip "%ZIP_NAME%" "%BUILD_DIR%\*"
) else (
    echo 7-Zip not found. Please manually compress the contents of the build folder.
    echo 1. Open the %BUILD_DIR% folder
    echo 2. Select all files and folders
    echo 3. Right-click and select "Send to" > "Compressed (zipped) folder"
    echo 4. Rename the zip file to %ZIP_NAME%
    explorer "%CD%\%BUILD_DIR%"
)

echo Build completed successfully!
echo Release package created or ready to be created manually.

endlocal 
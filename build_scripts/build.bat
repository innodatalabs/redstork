: Variables to provide:
: GYP_MSVS_VERSION = 2017 | 2015
: CONFIGURATION = Debug | Release
: PLATFORM = x86 | x64
: PDFium_BRANCH = master | chromium/3211 | ...
: PDFium_V8 = enabled

: Input
set WindowsSDK_DIR=C:\Program Files (x86)\Windows Kits\10\bin\%PLATFORM%
set DepotTools_URL=https://storage.googleapis.com/chrome-infra/depot_tools.zip
set DepotTools_DIR=%CD%\depot_tools
set PDFium_URL=https://pdfium.googlesource.com/pdfium.git
set PDFium_SOURCE_DIR=%CD%\pdfium
set PDFium_BUILD_DIR=%PDFium_SOURCE_DIR%\out
set PDFium_PATCH_DIR=%CD%\patches
set PDFium_EXTRASRC=%CD%
set PDFium_CMAKE_CONFIG=%CD%\PDFiumConfig.cmake
set PDFium_ARGS=%CD%\src\args.windows.Release.gn

: Output
set PDFium_STAGING_DIR=%CD%\staging
set PDFium_INCLUDE_DIR=%PDFium_STAGING_DIR%\include
set PDFium_BIN_DIR=%PDFium_STAGING_DIR%\%PLATFORM%\bin
set PDFium_LIB_DIR=%PDFium_STAGING_DIR%\%PLATFORM%\lib
set PDFium_RES_DIR=%PDFium_STAGING_DIR%\%PLATFORM%\res
set PDFium_ARTIFACT_BASE=%CD%\pdfium-windows-%PLATFORM%
set PDFium_ARTIFACT=%PDFium_ARTIFACT_BASE%.zip

echo on

: Prepare directories
mkdir %PDFium_BUILD_DIR%
mkdir %PDFium_STAGING_DIR%
mkdir %PDFium_BIN_DIR%
mkdir %PDFium_LIB_DIR%

: Download depot_tools
call curl -fsSL -o depot_tools.zip %DepotTools_URL% || exit /b
call 7z -bd -y x depot_tools.zip -o%DepotTools_DIR% || exit /b
set PATH=%DepotTools_DIR%;%WindowsSDK_DIR%;%PATH%
set DEPOT_TOOLS_WIN_TOOLCHAIN=0

: check that rc.exe is in PATH
where rc.exe || exit /b

: Clone
call gclient config --unmanaged %PDFium_URL% || exit /b
call gclient sync || exit /b

: Checkout branch (or ignore if it doesn't exist)
echo on
cd %PDFium_SOURCE_DIR%
git.exe checkout %PDFium_BRANCH% && call gclient sync

: Install python packages
where python
call %DepotTools_DIR%\python.bat -m pip install pywin32 || exit /b

: Patch
cd %PDFium_SOURCE_DIR%
patch -p0 -i "%PDFium_PATCH_DIR%\BUILD.gn.diff" || exit /b
rem git.exe -C build apply -v "%PDFium_PATCH_DIR%\rc_compiler.patch" || exit /b


: Configure
copy %PDFium_ARGS% %PDFium_BUILD_DIR%\args.gn
REM if "%CONFIGURATION%"=="Release" echo is_debug=false >> %PDFium_BUILD_DIR%\args.gn
REM if "%PLATFORM%"=="x86" echo target_cpu="x86" >> %PDFium_BUILD_DIR%\args.gn
mkdir %PDFium_SOURCE_DIR%\redstork
mkdir %PDFium_SOURCE_DIR%\redstork\src
copy %PDFium_EXTRASRC%\src\* %PDFium_SOURCE_DIR%\redstork\src
copy %PDFium_EXTRASRC%\BUILD.gn %PDFium_SOURCE_DIR%\redstork\

: Generate Ninja files
call gn gen %PDFium_BUILD_DIR% || exit /b

: Build
call ninja -C %PDFium_BUILD_DIR% pdfium || exit /b

: Install
cd %PDFium_EXTRASRC%
C:\Pyton3.8\python.exe -m venv .venv
call .venv\Script\activate.bat
pip install wheel pytest

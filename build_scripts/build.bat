: Variables to provide:
: GYP_MSVS_VERSION = 2017 | 2015
: CONFIGURATION = Debug | Release
: PLATFORM = x86 | x64
: PDFium_BRANCH = master | chromium/3211 | ...
: PDFium_V8 = enabled

set WindowsSDK_DIR=C:\Program Files (x86)\Windows Kits\10\bin\%PLATFORM%

set REDSTORK=%CD%
set REDSTAGING=%CD%\staging
set /P PDFIUM_VERSION=< redstork\pdfium_version.txt

mkdir %REDSTAGING%
mkdir %REDSTAGING%\out
cd %REDSTAGING%
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
set PATH=%REDSTAGING%\depot_tools;%WindowsSDK_DIR%;%PATH%
set DEPOT_TOOLS_WIN_TOOLCHAIN=0

: check that rc.exe is in PATH
where rc.exe || exit /b

: Clone
call gclient config --unmanaged https://pdfium.googlesource.com/pdfium.git || exit /b
call gclient sync || exit /b

: Checkout branch (or ignore if it doesn't exist)
echo on
cd %REDSTAGING%\pdfium
git.exe checkout %PDVIUM_VERSION% || exit /b
call gclient sync || exit /b

: Install python packages
where python || exit /b
call %REDSTAGING%\depot_tools\python.bat -m pip install pywin32 || exit /b

: Patch
cd %REDSTAGING%\pdfium
patch -p0 -i %REDSTORK%\patches\BUILD.gn.diff

: Configure
copy %REDSTORK%\src\args.windows.Release.gn %REDSTAGING%\out\args.gn
REM if "%CONFIGURATION%"=="Release" echo is_debug=false >> %PDFium_BUILD_DIR%\args.gn
REM if "%PLATFORM%"=="x86" echo target_cpu="x86" >> %PDFium_BUILD_DIR%\args.gn

mkdir %REDSTAGING%\pdfium\redstork
mkdir %REDSTAGING%\pdfium\redstork\src
copy %REDSTORK%\src\* %REDSTAGING%\pdfium\redstork\src\ || exit /b
copy %REDSTORK%\BUILD.gn %REDSTAGING%\pdfium\redstork\ || exit /b

: Generate Ninja files
call gn gen %REDSTAGING%\out || exit /b

: Build
call ninja -C %REDSTAGING%\out || exit /b

cd %REDSTORK%
C:\Python38-x64\python.exe -m venv .venv
call .venv\Scripts\activate.bat
pip install pytest wheel

copy %REDSTAGING%\out\lib\redstork.dll.lib redstork\windows\ || exit /b
copy %REDSTAGING%\out\lib\redstork.dll redstork\windows\ || exit /b
set PYTHONPATH=.
pytest redstork\test  || exit /b

rd /s /q buid dist
python setup.py bdist_wheel

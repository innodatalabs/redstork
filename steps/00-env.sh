ROOT=${BUILD_ROOT:-$PWD/pdfium-build}

export PDFium_BUILD_ROOT=$ROOT
export PDFium_SOURCE_DIR=$ROOT/pdfium
export PDFium_BUILD_DIR=$ROOT/pdfium/out

export PDFium_TARGET_OS=linux
export OS=linux
export PDFium_TARGET_CPU=x64
export DEPOT_TOOLS_WIN_TOOLCHAIN=0


ROOT=${BUILD_ROOT:-$PWD/pdfium-build}

export PDFium_BUILD_ROOT=$ROOT
export PDFium_SOURCE_DIR=$ROOT/pdfium
export PDFium_BUILD_DIR=$ROOT/pdfium/out

export OS=${PDFium_TARGET_OS:?}
CPU=${PDFium_TARGET_CPU:?}
export DEPOT_TOOLS_WIN_TOOLCHAIN=0


ROOT=${BUILD_ROOT:-$PWD/pdfium-build}

export PDFium_BUILD_ROOT=$ROOT
export PDFium_SOURCE_DIR=$ROOT/pdfium
export PDFium_BUILD_DIR=$ROOT/pdfium/out
export PDFium_IS_DEBUG=true

export OS=${PDFium_TARGET_OS:?}
export TARGET_CPU=${PDFium_TARGET_CPU:?}
export CURRENT_CPU=x64
export DEPOT_TOOLS_WIN_TOOLCHAIN=0


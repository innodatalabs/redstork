ROOT=${BUILD_ROOT:-$PWD/pdfium-build}

export PDFium_BUILD_ROOT=$ROOT
export PDFium_SOURCE_DIR=$ROOT/pdfium
export PDFium_BUILD_DIR=$ROOT/pdfium/out

export PDFium_IS_DEBUG=${PDFium_IS_DEBUG:?}
export OS=${PDFium_TARGET_OS:?}
export TARGET_CPU=${PDFium_TARGET_CPU:?}
export CURRENT_CPU=x64
export DEPOT_TOOLS_WIN_TOOLCHAIN=0

DEFAULT_BRANCH=`git ls-remote --heads https://pdfium.googlesource.com/pdfium.git | grep -ohP 'chromium/\d+' | tail -n1`
export PDFium_BRANCH=${PDFium_BRANCH:-$DEFAULT_BRANCH}



#!/bin/bash -eux

BUILD=${PDFium_BUILD_DIR:-pdfium/out}

STAGING=${PDFium_STAGING_DIR:-./staging}
STAGING_LIB="$STAGING/lib"
STAGING_BIN="$STAGING/bin"

mkdir -p "$STAGING"
mkdir -p "$STAGING_LIB"

case "$OS" in
  android|linux)
    mv "$BUILD/libpdfium.so" "$STAGING_LIB/libredstork.so"
    ;;

  mac|ios)
    mv "$BUILD/libpdfium.dylib" "$STAGING_LIB/libredstork.dylib"
    ;;

  win)
    mv "$BUILD/pdfium.dll.lib" "$STAGING_LIB/redstork.dll.lib"
    mkdir -p "$STAGING_BIN"
    mv "$BUILD/pdfium.dll" "$STAGING_BIN/redstork.dll"
    # [ "$IS_DEBUG" == "true" ] && mv "$BUILD/pdfium.dll.pdb" "$STAGING_BIN"
    ;;
esac

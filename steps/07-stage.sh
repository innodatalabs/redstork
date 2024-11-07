#!/bin/bash -eux

BUILD=${PDFium_BUILD_DIR:-pdfium/out}

STAGING=${PDFium_STAGING_DIR:-./redstork}
STAGING_LIB="$STAGING/$OS"
STAGING_BIN="$STAGING/$OS"

mkdir -p "$STAGING"
mkdir -p "$STAGING_LIB"

echo $STAGING_LIB
pwd

case "$OS" in
  android|linux)
    cp "$BUILD/libpdfium.so" "$STAGING_LIB/libredstork.so"
    ;;

  mac|ios)
    cp "$BUILD/libpdfium.dylib" "$STAGING_LIB/libredstork.dylib"
    ;;

  win)
    cp "$BUILD/pdfium.dll.lib" "$STAGING_LIB/redstork.dll.lib"
    mkdir -p "$STAGING_BIN"
    cp "$BUILD/pdfium.dll" "$STAGING_BIN/redstork.dll"
    # [ "$IS_DEBUG" == "true" ] && mv "$BUILD/pdfium.dll.pdb" "$STAGING_BIN"
    ;;
esac

#!/bin/bash -eux

SOURCE=${PDFium_SOURCE_DIR:-pdfium}
BUILD_DIR=${PDFium_BUILD_DIR:-$SOURCE/out}
TARGET_CPU=${PDFium_TARGET_CPU:?}
IS_DEBUG=${PDFium_IS_DEBUG:-false}

PATH=$PATH:$PDFium_BUILD_ROOT/pdfium/third_party/ninja
echo $PATH

ninja -C "$BUILD_DIR" pdfium

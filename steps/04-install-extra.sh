#!/bin/bash -eux

SOURCE="${PDFium_SOURCE_DIR:-pdfium}"
OS="${PDFium_TARGET_OS:?}"
CPU="${PDFium_TARGET_CPU:?}"

PATH=$PATH:$PDFium_BUILD_ROOT/depot_tools

pushd "$SOURCE"

case "$OS" in
    linux)
        # build/install-build-deps.sh
        # gclient runhooks
        # build/linux/sysroot_scripts/install-sysroot.py "--arch=$CPU"
        ;;
esac

popd
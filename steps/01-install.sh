#!/bin/bash -eux

PATH_FILE=${GITHUB_PATH:-$PDFium_BUILD_ROOT/.path}
TARGET_OS=${PDFium_TARGET_OS:?}

DepotTools_URL='https://chromium.googlesource.com/chromium/tools/depot_tools.git'
DepotTools_DIR="$PDFium_BUILD_ROOT/depot_tools"
WindowsSDK_DIR="/c/Program Files (x86)/Windows Kits/10/bin/10.0.19041.0"

# Download depot_tools if not exists in this location
if [ ! -d "$DepotTools_DIR" ]; then
    git clone "$DepotTools_URL" "$DepotTools_DIR"
fi

echo "$DepotTools_DIR" >> "$PATH_FILE"

case "$TARGET_OS" in
    linux)
        sudo apt-get update
        sudo apt-get install -y cmake pkg-config lsb-release g++
        ;;

    win)
        echo "$WindowsSDK_DIR/$CURRENT_CPU" >> "$PATH_FILE"
        ;;
esac
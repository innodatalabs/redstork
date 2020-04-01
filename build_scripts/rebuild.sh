# exit on error and do long report
set -ex

cd pdfium/pdfium_red

export PATH=$PATH:/depot_tools
ninja -C out/Debug
ninja -C out/Release

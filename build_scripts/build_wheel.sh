# exit on error and do long report
set -ex

cd pdfium/pdfium_red

export PATH=$PATH:/depot_tools
ninja -C out/Debug
ninja -C out/Release

cp out/Release/lib*.so /python_build/red/linux/
cd /python_build
rm -rf build dist
python setup.py bdist_wheel

cp dist/*.whl /out


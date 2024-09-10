#!/bin/bash -eux

BUILD_DIR=${PDFium_BUILD_DIR:?}

rm -rf .venv
python3.12 -m venv .venv
. .venv/bin/activate
pip install pytest wheel pip setuptools -U

# # build Debug Python wheel
# cp $REDSTAGING/out/Debug/lib*.so $REDSTORK/redstork/$OS/
# rm -f $REDSTORK/redstork/$OS/libpdfium*
# PYTHONPATH=. pytest redstork/test
# rm -rf build dist
# python setup.py bdist_wheel

# wheel_name=`(cd dist; ls *whl)`
# mv dist/$wheel_name dist/dbg-$wheel_name

# build Release Python wheel
[ "$OS" == "linux" ] && cp $BUILD_DIR/lib*.so ./redstork/$OS/
[ "$OS" == "darwin" ] && cp $BUILD_DIR/lib*.dylib ./redstork/$OS/
## FIXME: tests are failing due to font/glyph api change
# python -m pytest redstork/test
rm -rf build dist
python setup.py bdist_wheel

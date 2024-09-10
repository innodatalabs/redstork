#!/bin/bash -eux

BUILD_DIR=${PDFium_BUILD_DIR:?}

rm -rf .venv
python3.12 -m venv .venv
. .venv/bin/activate
pip install pytest wheel pip setuptools -U


STAGING=${PDFium_STAGING_DIR:-./staging}
STAGING_LIB="$STAGING/lib"
STAGING_BIN="$STAGING/bin"

mkdir -p "$STAGING"
mkdir -p "$STAGING_LIB"

case "$OS" in
  android|linux)
    cp "$STAGING_LIB/libredstork.so" "./redstork/$OS/"
    ;;

  mac|ios)
    cp "$STAGING_LIB/libredstork.dylib" "./redstork/$OS/"
    ;;

  win)
    cp "$STAGING_BIN/redstork.dll" "./redstork/$OS/"
    ;;
esac

# # build Debug Python wheel
# cp $REDSTAGING/out/Debug/lib*.so $REDSTORK/redstork/$OS/
# rm -f $REDSTORK/redstork/$OS/libpdfium*
# PYTHONPATH=. pytest redstork/test
# rm -rf build dist
# python setup.py bdist_wheel

# wheel_name=`(cd dist; ls *whl)`
# mv dist/$wheel_name dist/dbg-$wheel_name

# build Release Python wheel

## FIXME: tests are failing due to font/glyph api change
# python -m pytest redstork/test
rm -rf build dist
python setup.py bdist_wheel

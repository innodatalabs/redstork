# 
# 
# 
# exit on error and do long report
set -ex

REDSTORK=$PWD
[ -z ${REDSTAGING+x} ] && REDSTAGING=$PWD/staging

OS=`python3 -c "import sys; print(sys.platform)"`
# which version of PDFium to use?
PDFIUM_VERSION=`cat $REDSTORK/redstork/pdfium_version.txt`

[ -d $REDSTAGING ] || mkdir $REDSTAGING
cd $REDSTAGING
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH=$REDSTAGING/depot_tools:$PATH

gclient config --name pdfium --unmanaged https://pdfium.googlesource.com/pdfium.git
gclient sync

# checkout the right branch
cd $REDSTAGING/pdfium
git fetch origin $version
git checkout $version
gclient sync

# apply patches
patch -p0 -i $REDSTORK/patches/BUILD.gn.diff

mkdir $REDSTAGING/out
if [ -z ${REDDEBUG+x} ]; then
    cp $REDSTORK/src/args.$OS.Release.gn $REDSTAGING/out/args.gn
else
    cp $REDSTORK/src/args.$OS.Debug.gn $REDSTAGING/out/args.gn
fi

# copy new sources
mkdir $REDSTAGING/pdfium/redstork
cp $REDSTORK/BUILD.gn $REDSTAGING/pdfium/redstork/
cp -r $REDSTORK/src $REDSTAGING/pdfium/redstork/src

# # build debug
# gn gen $REDSTAGING/out/Debug
# ninja -C $REDSTAGING/out/Debug

# build release
gn gen $REDSTAGING/out
ninja -C $REDSTAGING/out

cd $REDSTORK
python3 -m venv .venv
. .venv/bin/activate
pip install pytest wheel

# # build Debug Python wheel
# cp $REDSTAGING/out/Debug/lib*.so $REDSTORK/redstork/$OS/
# rm -f $REDSTORK/redstork/$OS/libpdfium*
# PYTHONPATH=. pytest redstork/test
# rm -rf build dist
# python setup.py bdist_wheel

# wheel_name=`(cd dist; ls *whl)`
# mv dist/$wheel_name dist/dbg-$wheel_name

# build Release Python wheel
[ "$OS" == "linux" ] && cp $REDSTAGING/out/lib*.so $REDSTORK/redstork/$OS/
[ "$OS" == "darwin" ] && cp $REDSTAGING/out/lib*.dylib $REDSTORK/redstork/$OS/
rm -f $REDSTORK/redstork/$OS/libpdfium*
PYTHONPATH=. pytest redstork/test
rm -rf build dist
python setup.py bdist_wheel

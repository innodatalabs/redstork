# exit on error and do long report
set -ex

# which version of PDFium to use?
version=`cat /self/redstork/pdfium_version.txt`

git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH=$PATH:/depot_tools

gclient config --name pdfium --unmanaged https://pdfium.googlesource.com/pdfium.git

# resolve third-party deps and download everything
gclient sync

# checkout the right branch
cd pdfium
git fetch origin $version
git checkout $version

# update again since we changed the version
gclient sync

# apply patches
patch -p0 -i /self/patches/BUILD.gn.diff
(cd build; patch -p0 -i /self/patches/gcc_solink_wrapper.py.diff)

# copy new sources
cp -r /self redstork

mkdir /out /out/Debug /out/Release
cp /self/src/args.Debug.gn /out/Debug/args.gn
cp /self/src/args.Release.gn /out/Release/args.gn

cd redstork

# build debug
gn gen /out/Debug
ninja -C /out/Debug

# build release
gn gen /out/Release
ninja -C /out/Release

# build Python wheel
cp /out/Release/lib*.so redstork/linux/
rm -rf build dist
python setup.py bdist_wheel
cp dist/*.whl /out

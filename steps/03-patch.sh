#!/bin/bash -eux

SRC=${PWD}

# apply patches
pushd $PDFium_SOURCE_DIR
git checkout .
git apply -v $SRC/patches/shared_library.patch

# copy new sources
rm -rf ./redstork
mkdir ./redstork
cp $SRC/BUILD.gn ./redstork/
cp -r $SRC/src ./redstork/src

echo "#define REDSTORK_VERSION \"$PDFium_BRANCH\"" > ./redstork/src/redstork_version.h

popd

# pdfium_red

PDF Parsing library, based on `pdfium` project.

## Preparation

### Tooling

Build tool-chain from Google includes:
* gclient
* ninja
* gn

```bash
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
```

You **must** add this directory to your path, best do this in your `~/.bashrc`
```
export PATH=$PATH;/home/mike/git/depot_tools
```

### PDFium

From this directory, do:
```bash
gclient config --name pdfium --unmanaged https://pdfium.googlesource.com/pdfium.git
gclient sync
```

### Checkout pdfium_red
From `pdfium` directory, do:

```bash
git clone github.com/innodatalabs/pdfium_red.git
```

### Apply patches

Patch root `BUILD.gn` file
```bash
patch -p0 -i pdfium_red/patches/BUILD.gn.diff
```

Patch build/toolchain for Python3 compatibility (if using Python3 as build engine)
```bash
(cd build; patch -p0 -i ../pdfium_red/patches/gcc_solink_wrapper.py.diff)
```

Note to myself: how to generate patch files
```bash
git diff --no-prefix >> filename.diff
```

### Generate ninja files

Use `gn` tool (from Google toolchain) to generate `ninja` files:
```
cd pdfium_red
mkdir out out/Debug out/Release
cp args.Debug.gn out/Debug/args.gn
cp args.Release.gn out/Release/args.gn
gn gen out/Debug
gn gen out/Release
```

Note: You can also set arguments interactively using `gn args out/Debug` command.
If so, use the following settings: (note that you may want to change `is_debug` fo `false`)
```gn
use_goma = false
is_debug = true

pdf_use_skia = false
pdf_use_skia_paths = false
pdf_enable_xfa = false
pdf_enable_v8 = false
is_component_build = true

clang_use_chrome_plugins = false
```

### Build
```bash
ninja -C out/Debug
```

# Lazy builds

## Build pre-compiled pdfium docker

```bash
docker build -t red69 -f docker/Dockerfile .
```

This takes a long time (downloads all deps and
compiles 1.5K sources for Debug and Release).

## Develop
```bash
docker run -v`pwd`:/pdfium/pdfium_red -it red69
make wheel
```

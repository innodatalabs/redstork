# pdfium_red

PDF Parsing library, based on `pdfium` project.

## Preparation

### Tooling

Build tool-chain from Google includes:
* ninja
* gn

```bash
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
```

You **must** this directory to your path, best do this in wout `~/.bashrc`
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

### Patch root `BUILD.gn` file
```bash
echo 'group("pdfium_red") { deps = [ "//pdfium_red" ] }' >> BUILD.gn
```

### Generate ninja files

Use `gn` tool (from Google toolchain) to generate `ninja` files:
```
cd pdfium_red
gn args out/Debug
```

Use the following settings: (note that you may want to change `is_debug`)
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


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
git clone https://pdfium.googlesource.com/pdfium.git
```

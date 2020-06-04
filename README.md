# redstork
[![Build Status](https://travis-ci.com/innodatalabs/redstork.svg?branch=master)](https://travis-ci.com/innodatalabs/redstork)
[![PyPI version](https://badge.fury.io/py/redstork.svg)](https://badge.fury.io/py/redstork)
[![Documentation Status](https://readthedocs.org/projects/red-stork/badge/?version=latest)](https://red-stork.readthedocs.io/en/latest/?badge=latest)

<p align="center"><img width="100" height="250" src="https://raw.githubusercontent.com/innodatalabs/redstork/master/graphics/redstork.svg"></p>

PDF Parsing library, based on [PDFium](https://pdfium.googlesource.com/pdfium/).

## Requirements

* Fairly recent Linux (Ubuntu 18.04 or better). Support for other platforms is in the works.
* Python 3

## Installation
```bash
pip install redstork
```

## Features

* Convert to an image - page or arbitrary rectangle - using configurable scale
* Update document meta
* Update font encoding (for some PDF documents)
* Save document to a file

## Quick start

Download a sample PDF file [from here](https://github.com/innodatalabs/redstork/blob/master/redstork/test/resources/sample.pdf)

```python
from redstork import Document, PageObject, Glyph

doc = Document('sample.pdf')

print('Number of pages:', len(doc))
>> Number of pages: 15

print('MediaBox of the first page is:', doc[0].media_box)
>> MediaBox of the first page is: (0.0, 0.0, 612.0, 792.0)

print('Rotation of the first page is:', doc[0].rotation)
>> Rotation of the first page is: 0

print('Document title:', doc.meta['Title'])
>> Document title: Red Stork

print('First page has', len(doc[0]), 'objects')
>> First page has 4 objects

doc[0].render('page-0.ppm', scale=2)   # render page #1 as image

page = doc[0]
for o in page:
    if o.type == PageObject.OBJ_TYPE_TEXT:
        for code, _, _ in o:
            print(o.font[code], end='')
        print()
>> RedStork
>> Release0.0.1
>> Apr02,2020

for fid, font in doc.fonts.items():
    print(font.short_name, fid)
>> NimbusSanL-Bold (36, 0)
>> NimbusSanL-BoldItal (37, 0)

# lets generate an SVG file of the first letter on page 1
text_object = [o for o in page if o.type == PageObject.OBJ_TYPE_TEXT][0]  # first text object
charcode, _, _ = text_object[0]  # first character of the first text object

glyph = font.load_glyph(charcode)
path, delayed_c = [], []
for x, y, op, close in glyph:
    x, y = round(x, 3), round(y, 3)
    if op == Glyph.MOVETO:
        path.append(f'M {x} {y}')
    elif op == Glyph.LINETO:
        path.append(f'L {x} {y}')
    elif op == Glyph.CURVETO:
        delayed_c.append(f'{x} {y}')
        if len(delayed_c) == 3:
            path.append('C ' + ', '.join(delayed_c))
            delayed_c.clear()
    if close:
        path.append('Z')
path = ' '.join(path)
print('<svg><g fill="gray" transform="scale(100,-100)"><path d="' + path + '" /></g></svg>')
>> <svg><g fill="gray" transform="scale(100,-100)"><path d="M 0.291 0.289 L 0.463 0.289 C 0.52 0.289, ... L 0.318 0.414 Z" /></g></svg>
```

## API docs

https://red-stork.readthedocs.io

# redstork
[![PyPI version](https://badge.fury.io/py/redstork.svg)](https://badge.fury.io/py/redstork)
[![Documentation Status](https://readthedocs.org/projects/red-stork/badge/?version=latest)](https://red-stork.readthedocs.io/en/latest/?badge=latest)

<p align="center"><img width="100" height="250" src="graphics/redstork.svg"></p>

PDF Parsing library, based on [PDFium](https://pdfium.googlesource.com/pdfium/).

## Requirements

* Fairly recent Linux (Ubuntu 18.04 or better). Support for other platforms is in the works.
* Python 3

## Installation
```bash
pip install redstork
```

## Quick start

Download a sample PDF file from here: https://github.com/innodatalabs/redstork/blob/master/redstork/test/resources/sample.pdf

```python
from redstork import Document

doc = Document('sample.pdf')

print('Number of pages:', len(doc))
>> Number of pages: 15

print('MediaBox of the first page is:', doc[0].media_box)
>> MediaBox of the first page is: (0.0, 0.0, 612.0, 792.0)

print('Rotation of the first page is:', doc[0].rotation)
>> Rotation of the first page is: 0

doc[0].render('page-0.ppm', scale=2)   # render page #1 as image
```

## API docs

https://red-stork.readthedocs.io

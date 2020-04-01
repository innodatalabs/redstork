__version__ = '0.0.1'

import os
with open(os.path.join(os.path.dirname(__file__), 'pdfium_version.txt')) as f:
    __pdfium_version__ = f.read().strip()


from .document import Document
from .page import Page
from .font import Font

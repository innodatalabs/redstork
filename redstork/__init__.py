__version__ = '0.0.9'

import os
with open(os.path.join(os.path.dirname(__file__), 'pdfium_version.txt')) as f:
    __pdfium_version__ = f.read().strip()


from .document import Document
from .page import Page
from .pageobject import PageObject, TextObject, ImageObject, PathObject, ShadingObject, FormObject
from .font import Font

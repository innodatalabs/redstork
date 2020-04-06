from ctypes import pointer, c_float
from .bindings import so, FPDF_RECT, FPDF_MATRIX
from .font import Font


class PageObject:
    '''Common superclass of all page objects'''
    def __init__(self, obj, index, typ, parent):
        self._obj = obj
        self._index = index
        self._parent = parent
        self.type = typ
        self.matrix = 1., 0., 0., 1., 0., 0.

    @property
    def rect(self):
        rect = FPDF_RECT(0., 0., 0., 0.)
        so.REDPageObject_GetRect(self._obj, pointer(rect))
        return rect.left, rect.bottom, rect.right, rect.top


class TextObject(PageObject):
    '''Represents a string of text on a page'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)
        f = so.REDTextObject_GetFont(obj)
        self.font = Font(f, self)                           #: :class:Font for this text object
        self.font_size = so.REDTextObject_GetFontSize(obj)  #: font size of this text object

        matrix = FPDF_MATRIX(1., 0., 0., 1., 0., 0.)
        so.FPDFTextObj_GetMatrix(obj, pointer(matrix))
        self.matrix = matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f  #: matrix for this page object

        matrix = FPDF_MATRIX(1., 0., 0., 1., 0., 0.)
        so.REDTextObject_GetTextMatrix(obj, pointer(matrix))
        self.text_matrix = matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f  #: text matrix for this page object

    def __len__(self):
        '''Number of items in this string'''
        return so.REDTextObject_CountItems(self._obj)

    def __getitem__(self, index):
        '''Returns item at this index.'''
        return RED_Char()

    def __iter__(self):
        '''Iterates over items.'''
        for i in range(len(self)):
            yield self[i]

    def __repr__(self):
        return f'<TextObject len={len(self)}, font_size={self.font_size}>'


class PathObject(PageObject):
    '''Represents vector graphics on a aage.'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)
        matrix = FPDF_MATRIX(1., 0., 0., 1., 0., 0.)
        so.FPDFPath_GetMatrix(obj, pointer(matrix))
        self.matrix = matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f  #: matrix for this page object

    def __repr__(self):
        return '<PathObject>'

class ImageObject(PageObject):
    '''Represents image on a page.'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)
        a = c_float(1.0)
        b = c_float(0.0)
        c = c_float(0.0)
        d = c_float(1.0)
        e = c_float(0.0)
        f = c_float(0.0)
        so.FPDFImageObj_GetMatrix(
            obj, pointer(a), pointer(b), pointer(c),
            pointer(c), pointer(c), pointer(c)
        )
        self.matrix = a.value, b.value, c.value, d.value, e.value, f.value  #: matrix for this page object

    def __repr__(self):
        return '<ImageObject>'

    @property
    def pixel_width(self):
        return so.REDImageObject_GetPixelWidth(self._obj)

    @property
    def pixel_height(self):
        return so.REDImageObject_GetPixelHeight(self._obj)

class ShadingObject(PageObject):
    '''Represents a shading object on a page.'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)

    def __repr__(self):
        return '<ShadingObject>'

class FormObject(PageObject):
    '''Represents interactive form on a page.'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)
        matrix = FPDF_MATRIX(1., 0., 0., 1., 0., 0.)
        so.FPDFFormObj_GetMatrix(obj, pointer(matrix))
        self.matrix = matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f  #: matrix for this page object

    def __repr__(self):
        return '<FormObject>'



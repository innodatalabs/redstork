from ctypes import pointer, c_float, byref
from .bindings import so, FPDF_RECT, FPDF_MATRIX, FPDF_ITEM_INFO
from .font import Font
import contextlib


class PageObject:
    OBJ_TYPE_TEXT    = 1  #: see :class:`TextObject`
    OBJ_TYPE_PATH    = 2  #: see :class:`PathObject`
    OBJ_TYPE_IMAGE   = 3  #: see :class:`ImageObject`
    OBJ_TYPE_SHADING = 4  #: see :class:`ShadingObject`
    OBJ_TYPE_FORM    = 5  #: for internal use only

    '''Common superclass of all page objects'''
    def __init__(self, obj, index, typ, parent):
        self._obj = obj
        self._index = index
        self._parent = parent
        self.type = typ                      #: type of this object
        self.matrix = 1., 0., 0., 1., 0., 0. #: transformation matrix of this object
        left, bottom, right, top = c_float(), c_float(), c_float(), c_float()
        rc = so.FPDFPageObj_GetBounds(self._obj,
            byref(left), byref(bottom), byref(right), byref(top))
        if not rc:
            raise RuntimeError('FPDFPageObj_GetBounds failed')
        self.rect = left.value, bottom.value, right.value, top.value  # object rectangle

    @property
    def page(self):
        '''Links back to the parent page'''
        return self._parent

    @classmethod
    def new(cls, obj, index, typ, parent):
        if typ == cls.OBJ_TYPE_TEXT:
            return TextObject(obj, index, typ, parent)
        elif typ == cls.OBJ_TYPE_PATH:
            return PathObject(obj, index, typ, parent)
        elif typ == cls.OBJ_TYPE_IMAGE:
            return ImageObject(obj, index, typ, parent)
        elif typ == cls.OBJ_TYPE_SHADING:
            return ShadingObject(obj, index, typ, parent)
        elif typ == cls.OBJ_TYPE_FORM:
            return FormObject(obj, index, typ, parent)
        else:
            raise RuntimeError('unexpected page object type %s' % typ)

    @contextlib.contextmanager
    def transform(self, matrix):
        saved = self.matrix
        self.matrix = compose(self.matrix, matrix)

        x0,y0,x1,y1 = self.rect
        vertices = [
            apply(matrix, (x0, y0)),
            apply(matrix, (x0, y1)),
            apply(matrix, (x1, y0)),
            apply(matrix, (x1, y1)),
        ]

        self.rect = min(x for x,_ in vertices), min(y for _,y in vertices), max(x for x,_ in vertices), max(y for _,y in vertices)

        try:
            yield
        finally:
            self.matrix = saved
            self.rect = x0, y0, x1, y1


class TextObject(PageObject):
    '''Represents a string of text on a page'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)

        f = so.REDTextObject_GetFont(obj)
        font = Font(f, parent)
        doc = parent.document
        self.font = doc.fonts.setdefault(font.id, font)  #: :class:`Font` for this text object
        self.font_size = so.FPDFTextObj_GetFontSize(obj)  #: font size of this text object

        matrix = FPDF_MATRIX(1., 0., 0., 1., 0., 0.)
        so.FPDFTextObj_GetMatrix(obj, pointer(matrix))
        self.matrix = matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f  #: matrix for this page object

    def __len__(self):
        '''Number of items in this string'''
        return so.REDTextObject_CountItems(self._obj)

    def __getitem__(self, index):
        '''Returns item at this index.

        Each item is a 3-tuple: (charcode, x, y).
        '''
        item = FPDF_ITEM_INFO(-1, 0., 0.)
        so.REDTextObject_GetItemInfo(self._obj, index, pointer(item))
        return item.code, item.x, item.y

    def __iter__(self):
        '''Iterates over items.'''
        for i in range(len(self)):
            yield self[i]

    def char_iter(self):
        '''Iterates over characters (skips kerns)'''
        for c, x, y in self:
            if c  != -1:  # -1 is kern
                yield c, x, y

    def text_geometry_iter(self):
        '''Iterates over characters and returns character text and bounds'''
        font = self.font
        a, b, c, d, e, f = self.matrix
        for cid, x, y in self.char_iter():
            text = font[cid]
            glyph = font.load_glyph(cid)
            if glyph is None:
                continue  # any better idea?
            ascent, descent, advance = glyph.ascent, glyph.descent, glyph.advance
            ascent  *= self.font_size
            descent *= self.font_size
            advance *= self.font_size
            box = self.box(x, y-descent, x+advance, y+ascent)

            yield text, box

    @property
    def effective_font_size(self):
        '''Returns effective (user-visible) font size'''
        return self.font_size * self.scale_y

    @property
    def scale_y(self):
        '''Returns Y-scale of text matrix transformation'''
        a, b, c, d, e, f = self.matrix
        #
        #   a  b
        #   c  d
        #
        # (1, 0) => (a, c)
        # (0, 1) => (b, d). Note that (d, -b) is orthogonal to (b, d)
        # (d, -b) * (a, c) / |(a,c)| / |(d,-b)| is a height correction due to skew
        # |(b,d)| is y-scale without skew correction
        # true y-scale is: (d,-b) * (a,c) / |(a,c)|
        return abs(a*d - b*c) / (math.sqrt(a*a + c*c) + 1.e-8)

    @property
    def scale_x(self):
        '''Returns X-scale of text matrix transformation'''
        a, b, c, d, e, f = self.matrix
        return math.sqrt(a*a + c*c)

    @property
    def skew(self):
        '''Returns skew value of text matrix.'''
        #
        #  a  b
        #  c  d
        #
        a, b, c, d, e, f = self.matrix
        return (a*b + c*d) / math.sqrt( (a*a + c*c) * (b*b + d*d) )

    def box(self, x0, y0, x1, y1):
        '''Computes bounding box after transformation with text matrix'''
        a, b, c, d, e, f = self.matrix
        vertices = [
            apply(self.matrix, (x0, y0)),
            apply(self.matrix, (x0, y1)),
            apply(self.matrix, (x1, y0)),
            apply(self.matrix, (x1, y1)),
        ]

        x0 = min(x for x,_ in vertices)
        x1 = max(x for x,_ in vertices)
        y0 = min(y for _,y in vertices)
        y1 = max(y for _,y in vertices)

        return x0, y0, x1, y1

    def __repr__(self):
        return f'<TextObject len={len(self)}, font_size={self.font_size}>'

    @property
    def text(self):
        font = self.font

        return ''.join(
            font[code]
            for code,_,_ in self.char_iter()
        )


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
        '''width of the bitmap, in pixels'''
        return so.REDImageObject_GetPixelWidth(self._obj)

    @property
    def pixel_height(self):
        '''height of the bitmap, in pixels'''
        return so.REDImageObject_GetPixelHeight(self._obj)

class ShadingObject(PageObject):
    '''Represents a shading object on a page.'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)

    def __repr__(self):
        return '<ShadingObject>'

class FormObject(PageObject):
    '''Represents a form (XObject) on a page - a container of other page objects (used internally).'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)
        matrix = FPDF_MATRIX(1., 0., 0., 1., 0., 0.)
        so.FPDFFormObj_GetMatrix(obj, pointer(matrix))
        self.matrix = (
            matrix.a, matrix.b, matrix.c,
            matrix.d, matrix.e, matrix.f
        )  #: matrix for this page object
        form_matrix = FPDF_MATRIX(1., 0., 0., 1., 0., 0.)
        so.REDFormObject_GetFormMatrix(obj, pointer(matrix))
        self.form_matrix = (
            form_matrix.a, form_matrix.b, form_matrix.c,
            form_matrix.d, form_matrix.e, form_matrix.f
        )  #: transformation matrix for contained objects

    def __len__(self):
        return so.FPDFFormObj_CountObjects(self._obj)

    def __getitem__(self, index):
        if index < 0:
            index = len(self) + index

        subobj = so.FPDFFormObj_GetObject(self._obj, index)
        typ    = so.FPDFPageObj_GetType(subobj)
        return PageObject.new(subobj, index, typ, self)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def flat_iter(self):
        '''Iterates over all non-container objects in this form.'''
        for obj in self:
            if obj.type == PageObject.OBJ_TYPE_FORM:
                yield from obj.flat_iter()
            else:
                with obj.transform(self.matrix):
                    yield obj

    def __repr__(self):
        return f'<FormObject len={len(self)}>'

    @property
    def document(self):
        return self._parent.document

def compose(m1, m0):
    a0, b0, c0, d0, e0, f0 = m0
    a1, b1, c1, d1, e1, f1 = m1

    a = a1*a0 + c1*b0
    b = b1*a0 + d1*c0
    c = a1*c0 + c1*d0
    d = b1*c0 + d1*d0
    e = e1*a0 + f1*b0 + e0
    f = e1*c0 + f1*d0 + f0

    return a, b, c, d, e, f

def apply(m, v):
    a, b, c, d, e, f = m
    x, y = v

    return e + a*x + c*y, f + b*x + d*y

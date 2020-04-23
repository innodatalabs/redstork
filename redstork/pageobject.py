from ctypes import pointer, c_float
from .bindings import so, FPDF_RECT, FPDF_MATRIX, FPDF_ITEM_INFO
from .font import Font


class PageObject:
    OBJ_TYPE_TEXT    = 1
    OBJ_TYPE_PATH    = 2
    OBJ_TYPE_IMAGE   = 3
    OBJ_TYPE_SHADING = 4
    OBJ_TYPE_FORM    = 5

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


class TextObject(PageObject):
    '''Represents a string of text on a page'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)
        f = so.REDTextObject_GetFont(obj)
        self.font = Font(f, parent)                         #: :class:`Font` for this text object
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

    def __repr__(self):
        return f'<TextObject len={len(self)}, font_size={self.font_size}>'

    @property
    def text(self):
        font = self.font

        return ''.join(
            font[code]
            for code,_,_ in self
            if code != -1  # -1 is kern
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
    '''Represents a form (XObject) on a page - a container of other page objects.'''
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
        return so.REDFormObject_GetObjectCount(self._obj)

    def __getitem__(self, index):
        if index < 0:
            index = len(self) + index

        subobj = so.REDFormObject_GetObjectAt(self._obj, index)
        typ    = so.REDPageObject_GetType(subobj)
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
                yield obj

    def __repr__(self):
        return f'<FormObject len={len(self)}>'



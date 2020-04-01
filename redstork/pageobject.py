from ctypes import pointer
from .bindings import so, FPDF_RECT
from .font import Font


class PageObject:
    '''Common superclass of all page objects'''
    def __init__(self, obj, index, typ, parent):
        self._obj = obj
        self._index = index
        self._parent = parent
        self.type = typ

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
        self.font = Font(f, self)
        self.font_size = so.REDTextObject_GetFontSize(obj)

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

    def __repr__(self):
        return '<PathObject>'

class ImageObject(PageObject):
    '''Represents image on a page.'''
    def __init__(self, obj, index, typ, parent):
        super().__init__(obj, index, typ, parent)

    def __repr__(self):
        return '<ImageObject>'

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

    def __repr__(self):
        return '<FormObject>'



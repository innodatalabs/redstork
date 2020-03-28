from ctypes import CDLL, pointer, POINTER, Structure, create_string_buffer, create_unicode_buffer
from ctypes import c_int, c_long, c_float, c_void_p, c_char_p

so = CDLL('out/Debug/libpdfium_red.so')

RED_InitLibrary = so.RED_InitLibrary
RED_DestroyLibrary = so.RED_DestroyLibrary

so.RED_LastError.restype = c_char_p

so.RED_LoadDocument.argtypes = [c_char_p, c_char_p]
so.RED_LoadDocument.restype = c_void_p

so.FPDF_CloseDocument.argtypes = [c_void_p]

so.FPDF_GetPageCount.argtypes = [c_void_p]
so.FPDF_GetPageCount.restype = c_int

so.FPDF_LoadPage.argtypes = [c_void_p, c_int]
so.FPDF_LoadPage.restype = c_void_p

so.FPDF_ClosePage.argtypes = [c_void_p]

so.FPDF_GetPageWidthF.argtypes = [c_void_p]
so.FPDF_GetPageWidthF.restype = c_float
so.FPDF_GetPageHeightF.argtypes = [c_void_p]
so.FPDF_GetPageHeightF.restype = c_float

class FPDF_RECT(Structure):
    _fields_ = [
        ('left', c_float),
        ('top', c_float),
        ('right', c_float),
        ('bottom', c_float),
    ]
so.FPDF_GetPageBoundingBox.argtypes = [c_void_p, POINTER(FPDF_RECT)]
so.FPDF_GetPageBoundingBox.restype = c_int

so.FPDFPage_GetMediaBox.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p ]
so.FPDFPage_GetMediaBox.restype = c_int

so.FPDFPage_GetCropBox.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p ]
so.FPDFPage_GetCropBox.restype = c_int

so.FPDF_GetMetaText.argtypes = [c_void_p, c_char_p, c_void_p, c_long]
so.FPDF_GetMetaText.restype = c_long

so.FPDF_GetPageLabel.argtypes = [c_void_p, c_int, c_void_p, c_long]
so.FPDF_GetPageLabel.restype = c_long

so.REDPage_GetPageRotation.argtypes = [c_void_p]
so.REDPage_GetPageRotation.restype = c_int

so.REDPage_GetPageObjectCount.argtypes = [c_void_p]
so.REDPage_GetPageObjectCount.restype = c_int

so.REDPage_GetPageObjectByIndex.argtypes = [c_void_p, c_int]
so.REDPage_GetPageObjectByIndex.restype = c_void_p

so.REDPageObject_GetRect.argtypes = [c_void_p, POINTER(FPDF_RECT)]

so.REDPageObject_GetType.argtypes = [c_void_p]
so.REDPageObject_GetType.restype = c_int

so.REDTextObject_CountItems.argtypes = [c_void_p]
so.REDTextObject_CountItems.restype = c_int

so.REDTextObject_GetFontSize.argtypes = [c_void_p]
so.REDTextObject_GetFontSize.restype = c_float

so.REDTextObject_GetFont.argtypes = [c_void_p]
so.REDTextObject_GetFont.restype = c_void_p

so.REDFont_Destroy.argtypes = [c_void_p]

so.REDFont_GetName.argtypes = [c_void_p, c_void_p, c_int]
so.REDFont_GetName.restype = c_int

so.REDFont_GetFlags.argtypes = [c_void_p]
so.REDFont_GetFlags.restype = c_int

so.REDFont_GetWeight.argtypes = [c_void_p]
so.REDFont_GetWeight.restype = c_int

class RED_Document:
    RED_InitLibrary()

    def __init__(self, fname, password=None):
        c_fname = create_string_buffer(fname.encode() + b'\0')
        c_password = create_string_buffer(password.encode() + b'\0') if password is not None else None

        self._fname = fname
        self._doc = so.RED_LoadDocument(c_fname, c_password)
        self.numpages = so.FPDF_GetPageCount(self._doc)

    def __del__(self):
        so.FPDF_CloseDocument(self._doc)

    def __getitem__(self, page_index):
        if 0 <= page_index < self.numpages:
            return RED_Page(so.FPDF_LoadPage(self._doc, page_index), page_index, self)
        raise ValueError('Page number %s is out of range: 0..%s' % (page_index, self.numpages))

    def get_page_label(self, page_index):
        out = create_string_buffer(4096)
        l = so.FPDF_GetPageLabel(self._doc, page_index, out, 4096)
        return out.raw[:l].decode('utf-16le')

    def get_meta_text(self, key):
        '''Valid keys: Title, Author, Subject, Keywords, Creator, Producer,
             CreationDate, or ModDate.
           For detailed explanations of these tags and their respective
           values, please refer to PDF Reference 1.6, section 10.2.1,
           'Document Information Dictionary'.
        '''
        out = create_string_buffer(512)
        l = so.FPDF_GetMetaText(self._doc, create_string_buffer(key.encode() + b'\0'), out, 512)
        return out.raw[:l].decode('utf-16le')


class RED_Page:
    OBJ_TYPE_TEXT    = 1
    OBJ_TYPE_PATH    = 2
    OBJ_TYPE_IMAGE   = 3
    OBJ_TYPE_SHADING = 4
    OBJ_TYPE_FORM    = 5

    def __init__(self, page, page_index, parent):
        self._page = page
        self._page_index = page_index
        self._parent = parent

    @property
    def width(self):
        return so.FPDF_GetPageWidthF(self._page)

    @property
    def height(self):
        return so.FPDF_GetPageHeightF(self._page)

    @property
    def bbox(self):
        rect = FPDF_RECT(0., 0., 0., 0.)
        if not so.FPDF_GetPageBoundingBox(self._page, pointer(rect)):
            err = so.RED_LastError()
            raise RuntimeError('internal error: ' + err)
        return rect.left, rect.top, rect.right, rect.bottom

    @property
    def crop_box(self):
        l = c_float(0.)
        b = c_float(0.)
        r = c_float(0.)
        t = c_float(0.)
        if not so.FPDFPage_GetCropBox(
            self._page,
            pointer(l),
            pointer(b),
            pointer(r),
            pointer(t),
        ):
            err = so.RED_LastError()
            raise RuntimeError('internal error: ' + err)
        return l.value, t.value, r.value, b.value

    @property
    def media_box(self):
        l = c_float(0.)
        b = c_float(0.)
        r = c_float(0.)
        t = c_float(0.)
        if not so.FPDFPage_GetMediaBox(
            self._page,
            pointer(l),
            pointer(b),
            pointer(r),
            pointer(t),
        ):
            err = so.RED_LastError()
            raise RuntimeError('internal error: ' + err)
        return l.value, t.value, r.value, b.value

    @property
    def rotation(self):
        return so.REDPage_GetPageRotation(self._page)

    @property
    def label(self):
        self._parent.get_page_label(self._page_index)

    def __del__(self):
        so.FPDF_ClosePage(self._page)

    def __len__(self):
        return so.REDPage_GetPageObjectCount(self._page)

    def __getitem__(self, index):
        obj = so.REDPage_GetPageObjectByIndex(self._page, index)
        typ = so.REDPageObject_GetType(obj)
        if typ == self.OBJ_TYPE_TEXT:
            return RED_TextObject(obj, index, self)
        elif typ == self.OBJ_TYPE_PATH:
            return RED_PathObject(obj, index, self)
        elif typ == self.OBJ_TYPE_IMAGE:
            return RED_ImageObject(obj, index, self)
        elif typ == self.OBJ_TYPE_SHADING:
            return RED_ShadingObject(obj, index, self)
        elif typ == self.OBJ_TYPE_SHADING:
            return RED_ShadingObject(obj, index, self)
        else:
            raise RuntimeError('unexpected page object type %s' % typ)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

class RED_PageObject:
    def __init__(self, obj, index, typ, parent):
        self._obj = obj
        self._index = index
        self._parent = parent
        self.type = typ

    @property
    def rect(self):
        rect = FPDF_RECT(0., 0., 0., 0.)
        so.REDPageObject_GetRect(self._obj, pointer(rect))
        return rect.left, rect.top, rect.right, rect.bottom


class RED_TextObject(RED_PageObject):
    def __init__(self, obj, index, parent):
        super().__init__(obj, index, RED_Page.OBJ_TYPE_TEXT, parent)
        f = so.REDTextObject_GetFont(obj)
        self.font = RED_Font(f)
        self.font_size = so.REDTextObject_GetFontSize(obj)

    def __len__(self):
        return so.REDTextObject_CountItems(self._obj)

    def __getitem__(self, index):
        return RED_Char()

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __repr__(self):
        return f'<RED_TextObject len={len(self)}, font_size={self.font_size}>'


class RED_PathObject(RED_PageObject):
    def __init__(self, obj, index, parent):
        super().__init__(obj, index, RED_Page.OBJ_TYPE_PATH, parent)

    def __repr__(self):
        return '<RED_PathObject>'

class RED_ImageObject(RED_PageObject):
    def __init__(self, obj, index, parent):
        super().__init__(obj, index, RED_Page.OBJ_TYPE_IMAGE, parent)

    def __repr__(self):
        return '<RED_ImageObject>'

class RED_ShadingObject(RED_PageObject):
    def __init__(self, obj, index, parent):
        super().__init__(obj, index, RED_Page.OBJ_TYPE_SHADING, parent)

    def __repr__(self):
        return '<RED_ShadingObject>'

class RED_FormObject(RED_PageObject):
    def __init__(self, obj, index, parent):
        super().__init__(obj, index, RED_Page.OBJ_TYPE_FORM, parent)

    def __repr__(self):
        return '<RED_FormObject>'


class RED_Font:
    # Font styles as defined in PDF 1.7 Table 5.20
    FLAGS_NORMAL = 0
    FLAGS_FIXED_PITCH = (1 << 0)
    FLAGS_SERIF = (1 << 1)
    FLAGS_SYMBOLIC = (1 << 2)
    FLAGS_SCRIPT = (1 << 3)
    FLAGS_NONSYMBOLIC = (1 << 5)
    FLAGS_ITALIC = (1 << 6)
    FLAGS_ALLCAP = (1 << 16)
    FLAGS_SMALLCAP = (1 << 17)
    FLAGS_FORCE_BOLD = (1 << 18)

    def __init__(self, font):
        self._font = font

    @property
    def name(self):
        buf = create_string_buffer(512)
        length = so.REDFont_GetName(self._font, buf, 512)
        return buf[:length].decode()

    @property
    def flags(self):
        return so.REDFont_GetFlags(self._font)

    @property
    def weight(self):
        return so.REDFont_GetWeight(self._font)

    def __del__(self):
        so.REDFont_Destroy(self._font)

    def __repr__(self):
        return f'<RED_Font name={self.name}, flags={self.flags:04x}, weight={self.weight}>'


if __name__ == '__main__':
    import os

    fname = os.path.expanduser('~/REDSync/testResources/izguts/9783642051104.pdf')

    # RED_InitLibrary()
    # print('Inited')

    doc = RED_Document(fname)
    print(doc.get_meta_text('Creator'))

    print(doc.numpages)
    for page_index in range(doc.numpages):
        print('Page:', page_index)
        page = doc[page_index]
        print(page, page.width, page.height, page.bbox, page.crop_box, page.media_box, page.label, page.rotation, len(page))
        for x in page:
            print(x.rect, x.type, x)
            if x.type == RED_Page.OBJ_TYPE_TEXT:
                print('\t', x.font)

    # RED_DestroyLibrary()
    # print('Destroyed')


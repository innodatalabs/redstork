from ctypes import pointer, c_float, c_char_p
from .bindings import so, FPDF_RECT, FPDF_MATRIX
from .pageobject import (
    RED_TextObject,
    RED_PathObject,
    RED_ImageObject,
    RED_ShadingObject,
    RED_FormObject
)


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
        return l.value, b.value, r.value, t.value

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
        return l.value, b.value, r.value, t.value

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
            return RED_TextObject(obj, index, typ, self)
        elif typ == self.OBJ_TYPE_PATH:
            return RED_PathObject(obj, index, typ, self)
        elif typ == self.OBJ_TYPE_IMAGE:
            return RED_ImageObject(obj, index, typ, self)
        elif typ == self.OBJ_TYPE_SHADING:
            return RED_ShadingObject(obj, index, typ, self)
        elif typ == self.OBJ_TYPE_SHADING:
            return RED_ShadingObject(obj, index, typ, self)
        else:
            raise RuntimeError('unexpected page object type %s' % typ)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def render_(self, file_name, scale=1.0):
        result = so.REDPage_Render(self._page, c_char_p(file_name.encode()), 1, scale)
        if result == 0:
            raise RuntimeError('Failed to render as ' + file_name)

    def render(self, file_name, scale=1.0, rect=None):
        '''Render page (or rectangle on the page) as PPM image file.

        * file_name - the name of the output file
        * scale - the scale to use (default is 1.0, which will 1pt => 1px)
            Here is an example of computing scale.
            - If screen is 72dpi, and we want image to show at "natural" scale (1in on PDF as 1in on screen),
                then use scale=1.0
            - if screen is 100dpi, then use scale=100/72
            - if screen is retina at 300dpi, use scale=300/72
            - naturally, if you want to "zoom-in" just use higher scale factor.
        * rect - rectangle on the page 4-tuple of (left, top, right, bottom) in PDF coordinates (bottom < top)
            if None, then page's `cbox` will be used for rendering.
        '''
        cx0, cy0, cx1, cy1 = self.crop_box
        x0, y0, x1, y1 = self.crop_box if rect is None else rect
        fs_rect = FPDF_RECT(x0, y1, x1, y0)

        fs_matrix = FPDF_MATRIX(scale, 0., 0., scale, -fs_rect.left * scale, -((cy1-cy0)-y1) * scale)

        cropper = FPDF_RECT(0, 0, (x1-x0) * scale + 0.5, (y1-y0) * scale + 0.5)
        result = so.REDPage_RenderRect(
            self._page, c_char_p(file_name.encode()), 1, 1., fs_matrix, cropper)
        if result == 0:
            raise RuntimeError('Failed to render as ' + file_name)

    def __repr__(self):
        return f'<REDPage len={len(self)}>'


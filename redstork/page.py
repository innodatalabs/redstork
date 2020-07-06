from ctypes import pointer, c_float, c_char_p, create_string_buffer, byref
from .bindings import so, FPDF_RECT, FPDF_MATRIX
from .pageobject import PageObject


class Page:
    '''Represents page of a PDF file.'''

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
            raise RuntimeError('internal error: %s' % err)
        return rect.left, rect.top, rect.right, rect.bottom

    @property
    def crop_box(self):
        '''Page crop box.'''
        left, bottom, right, top = c_float(), c_float(), c_float(), c_float()

        mediabox = self.media_box
        rc = so.FPDFPage_GetCropBox(self._page,
            byref(left), byref(bottom), byref(right), byref(top))
        if rc:
            cropbox = left.value, bottom.value, right.value, top.value
        else:
            cropbox = mediabox

        x0 = max(cropbox[0], mediabox[0])
        x1 = min(cropbox[2], mediabox[2])
        y0 = max(cropbox[1], mediabox[1])
        y1 = min(cropbox[3], mediabox[3])

        assert x0 < x1 and y0 < y1

        return x0, y0, x1, y1

    @property
    def media_box(self):
        '''Page media box.'''
        left, bottom, right, top = c_float(), c_float(), c_float(), c_float()

        rc = so.FPDFPage_GetMediaBox(self._page,
            byref(left), byref(bottom), byref(right), byref(top))
        if not rc:
            return (0, 0, 612, 792)

        return left.value, bottom.value, right.value, top.value

    @property
    def rotation(self):
        '''Page rotation.

        * 0 - no rotation
        * 1 - rotated 90 degrees clock-wise
        * 2 - rotated 180 degrees clock-wise
        * 3 - rotated 270 degrees clock-wise
        '''
        return so.FPDFPage_GetRotation(self._page)

    @property
    def label(self):
        '''Page label.'''
        return self._parent._get_page_label(self._page_index)

    def __del__(self):
        so.FPDF_ClosePage(self._page)

    def __len__(self):
        '''Number of objects on this page.'''
        return so.FPDFPage_CountObjects(self._page)

    def __getitem__(self, index):
        '''Get object at this index.'''
        obj = so.FPDFPage_GetObject(self._page, index)
        typ = so.FPDFPageObj_GetType(obj)
        return PageObject.new(obj, index, typ, self)

    def __iter__(self):
        '''Iterates over page objects.'''
        for i in range(len(self)):
            yield self[i]

    def flat_iter(self):
        '''Iterates over all non-container objects (Text, Image, Path).'''
        for obj in self:
            if obj.type == PageObject.OBJ_TYPE_FORM:
                yield from obj.flat_iter()
            else:
                yield obj

    @staticmethod
    def _get_matrix(rotation, crop_box, rect, scale):
        '''PDFium renderer "conveniently" auto-rotates according to page.rotation value.
        We want to render page in native coordinate system (so that we can, for example,
        use word box coordinates to render the word). Hence we have to undo the "clever"
        transform that PDFium engine applies.
        '''
        cx0, cy0, cx1, cy1 = crop_box
        x0, y0, x1, y1 = rect
        #
        if rotation == 0:
            matrix = (scale, 0., 0., scale, (cx0-x0) * scale, (y1-cy1) * scale)
        elif rotation == 1:
            matrix = (0., -scale, scale, 0., (cx0-x0) * scale, (y1-cy0) * scale)
        elif rotation == 2:
            matrix = (-scale, 0., 0., -scale, (cx1-x0) * scale, (y1-cy0) * scale)
        elif rotation == 3:
            matrix = (0., scale, -scale, 0., (cx1-x0) * scale, (y1-cy1) * scale)
        else:
            raise RuntimeError('Unexpected rotation value: %s' % rotation)
        return matrix

    def render_to_buffer(self, scale=1.0, rect=None):
        '''Render page (or rectangle on the page) to memory (the pixel format is BGRx)

        Args:
            scale (float):      scale to use (default is 1.0, which will assume that 1pt takes 1px)
            rect (tuple):       optional rectangle to render. Value is a 4-tuple of (x0, y0, x1, y1) in PDF coordinates.
                                if None, then page's :attr:`crop_box` will be used for rendering.
        '''
        x0, y0, x1, y1 = self.crop_box if rect is None else rect
        fs_matrix = FPDF_MATRIX(*self._get_matrix(self.rotation, self.crop_box, (x0, y0, x1, y1), scale))

        width = int((x1 - x0) * scale + 0.5)
        height = int((y1 - y0) * scale + 0.5)
        cropper = FPDF_RECT(0, 0, width, height)

        buf_size = width * height * 4
        buf = create_string_buffer(buf_size)
        result = so.REDPage_RenderRect_Buffer(self._page, 1., fs_matrix, cropper, buf, buf_size)
        if result == 0:
            raise RuntimeError('Failed in rendering')

        return buf, width, height

    def render(self, file_name, scale=1.0, rect=None):
        '''Render page (or rectangle on the page) as PPM image file.

        Args:
            file_name (str):    name of the output file
            scale (float):      scale to use (default is 1.0, which will assume that 1pt takes 1px)
            rect (tuple):       optional rectangle to render. Value is a 4-tuple of (x0, y0, x1, y1) in PDF coordinates.
                                if None, then page's :attr:`crop_box` will be used for rendering.
        '''
        x0, y0, x1, y1 = self.crop_box if rect is None else rect
        fs_matrix = FPDF_MATRIX(*self._get_matrix(self.rotation, self.crop_box, (x0, y0, x1, y1), scale))

        width = int((x1 - x0) * scale + 0.5)
        height = int((y1 - y0) * scale + 0.5)
        cropper = FPDF_RECT(0, 0, width, height)
        result = so.REDPage_RenderRect(
            self._page, c_char_p(file_name.encode()), 1, 1., fs_matrix, cropper)
        if result == 0:
            raise RuntimeError('Failed to render as ' + file_name)

    @property
    def document(self):
        return self._parent

    def __repr__(self):
        return f'<Page len={len(self)}>'


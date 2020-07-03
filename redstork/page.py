from ctypes import pointer, c_float, c_char_p, create_string_buffer
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
        rect = FPDF_RECT(0., 0., 0., 0.)

        so.REDPage_GetCropBox(
            self._page,
            pointer(rect)
        )

        return rect.left, rect.bottom, rect.right, rect.top

    @property
    def media_box(self):
        '''Page media box.'''
        rect = FPDF_RECT(0., 0., 0., 0.)

        so.REDPage_GetMediaBox(
            self._page,
            pointer(rect)
        )

        return rect.left, rect.bottom, rect.right, rect.top

    @property
    def rotation(self):
        '''Page rotation.

        * 0 - no rotation
        * 1 - rotated 90 degrees clock-wise
        * 2 - rotated 180 degrees clock-wise
        * 3 - rotated 270 degrees clock-wise
        '''
        return so.REDPage_GetPageRotation(self._page)

    @property
    def label(self):
        '''Page label.'''
        return self._parent._get_page_label(self._page_index)

    def __del__(self):
        so.FPDF_ClosePage(self._page)

    def __len__(self):
        '''Number of objects on this page.'''
        return so.REDPage_GetPageObjectCount(self._page)

    def __getitem__(self, index):
        '''Get object at this index.'''
        obj = so.REDPage_GetPageObjectByIndex(self._page, index)
        typ = so.REDPageObject_GetType(obj)
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

    def render_(self, file_name, scale=1.0):
        result = so.REDPage_Render(self._page, c_char_p(file_name.encode()), 1, scale)
        if result == 0:
            raise RuntimeError('Failed to render as ' + file_name)

    def _get_fsmatrix(self, rotation, crop_box, rect, scale):
        '''
        get the fs_matrix based on the crop_box and rotatoin of the page, 
        and also the current region of interest (rect) and scaling
        '''
        cx0, cy0, cx1, cy1 = crop_box
        x0, y0, x1, y1 = rect
        # 
        if rotation == 0:
            fs_matrix = FPDF_MATRIX(scale, 0., 0., scale, -(x0-cx0) * scale, -(cy1-y1) * scale)
        elif rotation == 1:
            fs_matrix = FPDF_MATRIX(0., -scale, scale, 0., (cx1-x1) * scale, (y1-cy0) * scale)
        elif rotation == 2:
            fs_matrix = FPDF_MATRIX(0., scale, scale, 0., 0., 0.)
        elif rotation == 3:
            fs_matrix = FPDF_MATRIX(0., scale, -scale, 0., (x1-cx0) * scale, (y0-cy0) * scale)
        else:
            raise RuntimeError('Unexpected rotationv alue: %s' % rotation)
        return fs_matrix

    def render_to_buffer(self, scale=1.0, rect=None):
        '''Render page (or rectangle on the page) to memory (the pixel format is BGRx)

        Args:
            scale (float):      scale to use (default is 1.0, which will assume that 1pt takes 1px)
            rect (tuple):       optional rectangle to render. Value is a 4-tuple of (x0, y0, x1, y1) in PDF coordinates.
                                if None, then page's :attr:`crop_box` will be used for rendering.
        '''
        rect = self.crop_box if rect is None else rect
        fs_matrix = self._get_fsmatrix(self.rotation, self.crop_box, rect, scale)

        width = int((rect[2] - rect[0]) * scale + 0.5)
        height = int((rect[3] - rect[1]) * scale + 0.5)
        cropper = FPDF_RECT(0, 0, width, height)

        buf_size = int(width * height * 4)
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
        rect = self.crop_box if rect is None else rect
        fs_matrix = self._get_fsmatrix(self.rotation, self.crop_box, rect, scale)

        cropper = FPDF_RECT(0, 0, (rect[2] - rect[0]) * scale + 0.5, (rect[3] - rect[1]) * scale + 0.5)
        result = so.REDPage_RenderRect(
            self._page, c_char_p(file_name.encode()), 1, 1., fs_matrix, cropper)
        if result == 0:
            raise RuntimeError('Failed to render as ' + file_name)

    @property
    def document(self):
        return self._parent

    def __repr__(self):
        return f'<Page len={len(self)}>'


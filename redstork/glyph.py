from .bindings import so, FPDF_PATH_POINT
from ctypes import pointer


class Glyph:

    LINETO    = 0
    BEZIER_TO = 1
    MOVETO    = 2

    def __init__(self, glyph, parent):
        self._glyph = glyph
        self._parent = parent

    def __len__(self):
        return so.REDGlyph_Size(self._glyph)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, i):
        point = FPDF_PATH_POINT()
        so.REDGlyph_Get(self._glyph, i, pointer(point))
        return point.x, point.y, point.type, point.close
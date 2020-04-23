from .bindings import so, FPDF_PATH_POINT
from ctypes import pointer


class Glyph:
    '''Represents Glyph drawing instructions'''

    LINETO    = 0  #: LineTo instruction
    BEZIER_TO = 1  #: BezierTo instruction
    MOVETO    = 2  #: MoveTo instruction

    def __init__(self, glyph, parent):
        self._glyph = glyph
        self._parent = parent

    def __len__(self):
        return so.REDGlyph_Size(self._glyph)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, i):
        '''Returns a 4-tuple representing this drawing instruction: (x, y, type, close).

        Args:
            i (int): index of the operator
        '''
        point = FPDF_PATH_POINT()
        so.REDGlyph_Get(self._glyph, i, pointer(point))
        return point.x, point.y, point.type, point.close
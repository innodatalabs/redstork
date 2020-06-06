from .bindings import so, FPDF_PATH_POINT, FPDF_RECT
from ctypes import pointer


class Glyph:
    '''Represents Glyph drawing instructions'''

    LINETO  = 0  #: LineTo instruction
    CURVETO = 1  #: CurveTo instruction
    MOVETO  = 2  #: MoveTo instruction

    def __init__(self, glyph, parent):
        self._glyph = glyph
        self._parent = parent
        self._bounds = None

    def __len__(self):
        return so.REDGlyph_Size(self._glyph)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, i):
        '''Returns a 4-tuple representing this drawing instruction: (x, y, type, close).

        Args:
            i (int): index of the instruction
        '''
        point = FPDF_PATH_POINT()
        so.REDGlyph_Get(self._glyph, i, pointer(point))
        return point.x, point.y, point.type, point.close

    # @memoize
    # def _bounds(self):
    #     if len(self) == 0:
    #         return None
    #     coords = [(x, y) for x, y, _, _ in self]
    #     xmin = min(x for x,_ in coords)
    #     xmax = max(x for x,_ in coords)
    #     ymin = min(y for _,y in coords)
    #     ymax = max(y for _,y in coords)

    #     return xmin, ymin, xmax, ymax

    def bounds(self):
        if self._bounds is None:
            rect = FPDF_RECT(0., 0., 0., 0.)
            so.REDGlyph_GetBounds(self._glyph, pointer(rect))
            self._bounds = rect.left, rect.bottom, rect.right, rect.top
        return self._bounds

    @property
    def ascent(self):
        bounds = self.bounds()
        return max(0, bounds[3])

    @property
    def descent(self):
        _, ymin, _, _ = self.bounds()
        return max(0, -ymin)

    @property
    def advance(self):
        _, _, xmax, _ = self.bounds()
        return max(0, xmax)

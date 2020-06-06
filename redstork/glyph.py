from .bindings import so, FPDF_PATH_POINT, FPDF_RECT
from .memoize import memoize
from ctypes import pointer


class Glyph:
    '''Represents Glyph drawing instructions'''

    LINETO  = 0  #: LineTo instruction
    CURVETO = 1  #: CurveTo instruction
    MOVETO  = 2  #: MoveTo instruction

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

    @memoize
    def bounds(self):
        rect = FPDF_RECT(0., 0., 0., 0.)
        so.REDGlyph_GetBounds(self._glyph, pointer(rect))
        return rect.left, rect.bottom, rect.right, rect.top

    @property
    @memoize
    def ascent(self):
        bounds = self.bounds()
        if bounds is None:
            return 0
        return max(0, bounds[3])

    @property
    @memoize
    def descent(self):
        bounds = self.bounds()
        if bounds is None:
            return 0
        _, ymin, _, _ = self.bounds()
        return max(0, -ymin)

    @property
    @memoize
    def advance(self):
        bounds = self.bounds()
        if bounds is None:
            return 0
        _, _, xmax, _ = self.bounds()
        return max(0, xmax)


from ctypes import Structure, c_float

class FPDF_RECT(Structure):
    _fields_ = [
        ('left', c_float),
        ('top', c_float),
        ('right', c_float),
        ('bottom', c_float),
    ]

# Matrix for transformation, in the form [a b c d e f], equivalent to:
#  | a  b  0 |
#  | c  d  0 |
#  | e  f  1 |
#
#  Translation is performed with [1 0 0 1 tx ty].
#  Scaling is performed with [sx 0 0 sy 0 0].
#  See PDF Reference 1.7, 4.2.2 Common Transformations for more.
class FPDF_MATRIX(Structure):
    _fields_ = [
        ('a', c_float),
        ('b', c_float),
        ('c', c_float),
        ('d', c_float),
        ('e', c_float),
        ('f', c_float),
    ]

try:
    from .so import so
except OSError:
    print('Failed to load shared library')
    so = None


import os
import sys
from ctypes import CDLL, pointer, POINTER, Structure, create_string_buffer, create_unicode_buffer
from ctypes import c_int, c_long, c_float, c_void_p, c_char_p

if sys.platform == 'linux':
    so_name = 'linux/libredstork.so'
else:
    raise RuntimeError('Unsupported platform: %s' % sys.platform)

so_name = os.path.join(os.path.dirname(__file__), so_name)

so = CDLL(so_name)

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

so.RED_LastError.restype = c_char_p

so.RED_LoadDocument.argtypes = [c_char_p, c_char_p]
so.RED_LoadDocument.restype = c_void_p

so.FPDF_CloseDocument.argtypes = [c_void_p]

so.REDDoc_GetMetaTextKeyCount.argtypes = [c_void_p]
so.REDDoc_GetMetaTextKeyCount.restype = c_int

so.REDDoc_GetMetaTextKeyAt.argtypes = [c_void_p, c_int]
so.REDDoc_GetMetaTextKeyAt.restype = c_char_p

so.FPDF_GetPageCount.argtypes = [c_void_p]
so.FPDF_GetPageCount.restype = c_int

so.FPDF_LoadPage.argtypes = [c_void_p, c_int]
so.FPDF_LoadPage.restype = c_void_p

so.FPDF_ClosePage.argtypes = [c_void_p]

so.FPDF_GetPageWidthF.argtypes = [c_void_p]
so.FPDF_GetPageWidthF.restype = c_float
so.FPDF_GetPageHeightF.argtypes = [c_void_p]
so.FPDF_GetPageHeightF.restype = c_float

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

so.REDPage_GetMediaBox.argtypes = [c_void_p, POINTER(FPDF_RECT)]
so.REDPage_GetMediaBox.restype = c_int

so.REDPage_GetCropBox.argtypes = [c_void_p, POINTER(FPDF_RECT)]
so.REDPage_GetCropBox.restype = c_int

so.REDPage_GetPageObjectCount.argtypes = [c_void_p]
so.REDPage_GetPageObjectCount.restype = c_int

so.REDPage_GetPageObjectByIndex.argtypes = [c_void_p, c_int]
so.REDPage_GetPageObjectByIndex.restype = c_void_p

so.REDPage_Render.argtypes = [c_void_p, c_char_p, c_int, c_float]
so.REDPage_Render.restype = c_int

so.REDPage_RenderRect.argtypes = [c_void_p, c_char_p, c_int, c_float, POINTER(FPDF_MATRIX), POINTER(FPDF_RECT)]
so.REDPage_RenderRect.restype = c_int

so.REDPageObject_GetRect.argtypes = [c_void_p, POINTER(FPDF_RECT)]

so.REDPageObject_GetType.argtypes = [c_void_p]
so.REDPageObject_GetType.restype = c_int

so.REDTextObject_CountItems.argtypes = [c_void_p]
so.REDTextObject_CountItems.restype = c_int

so.REDTextObject_GetFontSize.argtypes = [c_void_p]
so.REDTextObject_GetFontSize.restype = c_float

so.REDTextObject_GetFont.argtypes = [c_void_p]
so.REDTextObject_GetFont.restype = c_void_p

so.FPDFTextObj_GetMatrix.argtypes = [c_void_p, POINTER(FPDF_MATRIX)]
so.FPDFTextObj_GetMatrix.restype = c_int

so.REDTextObject_GetTextMatrix.argtypes = [c_void_p, POINTER(FPDF_MATRIX)]
so.REDTextObject_GetTextMatrix.restype = c_int

so.REDFont_Destroy.argtypes = [c_void_p]

so.REDFont_GetName.argtypes = [c_void_p, c_void_p, c_int]
so.REDFont_GetName.restype = c_int

so.REDFont_GetFlags.argtypes = [c_void_p]
so.REDFont_GetFlags.restype = c_int

so.REDFont_GetWeight.argtypes = [c_void_p]
so.REDFont_GetWeight.restype = c_int

so.RED_InitLibrary()

so.REDImageObject_GetPixelWidth.argtypes = [c_void_p]
so.REDImageObject_GetPixelWidth.restype  = c_int

so.REDImageObject_GetPixelHeight.argtypes = [c_void_p]
so.REDImageObject_GetPixelHeight.restype  = c_int

so.FPDFImageObj_GetMatrix.argtypes = [
    c_void_p, POINTER(c_float), POINTER(c_float), POINTER(c_float),
    POINTER(c_float), POINTER(c_float), POINTER(c_float)
]
so.FPDFImageObj_GetMatrix.restype = c_int

so.FPDFPath_GetMatrix.argtypes = [c_void_p, POINTER(FPDF_MATRIX)]
so.FPDFPath_GetMatrix.restype = c_int

so.FPDFFormObj_GetMatrix.argtypes = [c_void_p, POINTER(FPDF_MATRIX)]
so.FPDFFormObj_GetMatrix.restype = c_int

import os
import sys
from ctypes import CDLL, pointer, POINTER, Structure, create_string_buffer, create_unicode_buffer
from ctypes import c_int, c_long, c_float, c_void_p, c_char_p, c_uint8, c_bool

if sys.platform == 'linux':
    so_name = 'linux/libredstork.so'
elif sys.platform == 'win32':
    so_name = 'win/redstork.dll'
elif sys.platform == 'darwin':
    so_name = 'darwin/libredstork.dylib'
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

class FPDF_ITEM_INFO(Structure):
    _fields_ = [
        ('code', c_int),
        ('x', c_float),
        ('y', c_float),
    ]

class FPDF_PATH_POINT(Structure):
    _fields_ = [
        ('x', c_float),
        ('y', c_float),
        ('type', c_uint8),
        ('close', c_bool),
    ]

so.RED_LastError.restype = c_char_p

so.FPDF_LoadDocument.argtypes = [c_char_p, c_char_p]
so.FPDF_LoadDocument.restype = c_void_p

so.FPDF_CloseDocument.argtypes = [c_void_p]

so.REDDoc_GetMetaTextKeyCount.argtypes = [c_void_p]
so.REDDoc_GetMetaTextKeyCount.restype = c_int

so.REDDoc_GetMetaTextKeyAt.argtypes = [c_void_p, c_int]
so.REDDoc_GetMetaTextKeyAt.restype = c_char_p

so.REDDoc_SetMetaItem.argtypes = [c_void_p, c_void_p, c_void_p]
so.REDDoc_SetMetaItem.restype = c_int

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

so.FPDFPage_GetRotation.argtypes = [c_void_p]
so.FPDFPage_GetRotation.restype = c_int

so.FPDFPage_CountObjects.argtypes = [c_void_p]
so.FPDFPage_CountObjects.restype = c_int

so.FPDFPage_GetObject.argtypes = [c_void_p, c_int]
so.FPDFPage_GetObject.restype = c_void_p

so.REDPage_Render.argtypes = [c_void_p, c_char_p, c_int, c_float]
so.REDPage_Render.restype = c_int

so.REDPage_RenderRect.argtypes = [c_void_p, c_char_p, c_int, c_float, POINTER(FPDF_MATRIX), POINTER(FPDF_RECT)]
so.REDPage_RenderRect.restype = c_int

so.REDPage_RenderRect_Buffer.argtypes = [c_void_p, c_float, POINTER(FPDF_MATRIX), POINTER(FPDF_RECT), c_char_p, c_int]
so.REDPage_RenderRect_Buffer.restype = c_int

so.FPDFPageObj_GetBounds.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p]
so.FPDFPageObj_GetBounds.restype = c_int

so.FPDFPageObj_GetType.argtypes = [c_void_p]
so.FPDFPageObj_GetType.restype = c_int

so.REDTextObject_CountItems.argtypes = [c_void_p]
so.REDTextObject_CountItems.restype = c_int

so.FPDFTextObj_GetFontSize.argtypes = [c_void_p]
so.FPDFTextObj_GetFontSize.restype = c_float

so.REDTextObject_GetFont.argtypes = [c_void_p]
so.REDTextObject_GetFont.restype = c_void_p

so.FPDFTextObj_GetMatrix.argtypes = [c_void_p, POINTER(FPDF_MATRIX)]
so.FPDFTextObj_GetMatrix.restype = c_int

so.REDTextObject_GetItemInfo.argtypes = [c_void_p, c_int, POINTER(FPDF_ITEM_INFO)]
so.REDTextObject_GetItemInfo.restype = c_int

so.FPDFFont_Close.argtypes = [c_void_p]
so.REDFont_GetName.argtypes = [c_void_p, c_void_p, c_int]
so.REDFont_GetName.restype = c_int

so.REDFont_GetFlags.argtypes = [c_void_p]
so.REDFont_GetFlags.restype = c_int

so.REDFont_GetWeight.argtypes = [c_void_p]
so.REDFont_GetWeight.restype = c_int

so.REDFont_GetId.argtypes = [c_void_p, c_void_p, c_void_p]
so.REDFont_GetId.restype = c_int

so.REDFont_IsVertical.argtypes = [c_void_p]
so.REDFont_IsVertical.restype = c_int

so.REDFont_UnicodeFromCharCode.argtypes = [c_void_p, c_int, c_void_p, c_int]
so.REDFont_UnicodeFromCharCode.restype = c_int

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

so.REDFormObject_GetFormMatrix.argtypes = [c_void_p, POINTER(FPDF_MATRIX)]
so.REDFormObject_GetFormMatrix.restype = c_int

so.FPDFFormObj_CountObjects.argtypes = [c_void_p]
so.FPDFFormObj_CountObjects.restype = c_int

so.FPDFFormObj_GetObject.argtypes = [c_void_p, c_int]
so.FPDFFormObj_GetObject.restype = c_void_p

so.REDFont_LoadGlyph.argtypes = [c_void_p, c_int]
so.REDFont_LoadGlyph.restype = c_void_p

so.REDGlyph_Size.argtypes = [c_void_p]
so.REDGlyph_Size.restype = c_int

so.REDGlyph_Get.argtypes = [c_void_p, c_int, POINTER(FPDF_PATH_POINT)]

so.REDFont_LoadUnicodeMap.argtypes = [c_void_p]
so.REDFont_LoadUnicodeMap.restype = c_void_p

so.REDFont_DestroyUnicodeMap.argtypes = [c_void_p]
so.REDFont_WriteUnicodeMap.argtypes = [c_void_p, c_void_p, c_int]
so.REDFont_WriteUnicodeMap.restype = c_int

so.REDDoc_Save.argtypes = [c_void_p, c_void_p]
so.REDDoc_Save.restype = c_int

so.REDGlyph_GetBounds.argtypes = [c_void_p, c_void_p]
so.REDGlyph_GetBounds.restype = c_int

so.RED_InitLibrary()

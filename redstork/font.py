from ctypes import create_string_buffer
from .bindings import so


class Font:
    # Font styles as defined in PDF 1.7 Table 5.20
    FLAGS_NORMAL = 0
    FLAGS_FIXED_PITCH = (1 << 0)
    FLAGS_SERIF = (1 << 1)
    FLAGS_SYMBOLIC = (1 << 2)
    FLAGS_SCRIPT = (1 << 3)
    FLAGS_NONSYMBOLIC = (1 << 5)
    FLAGS_ITALIC = (1 << 6)
    FLAGS_ALLCAP = (1 << 16)
    FLAGS_SMALLCAP = (1 << 17)
    FLAGS_FORCE_BOLD = (1 << 18)

    def __init__(self, font, parent):
        self._font = font
        self._parent = parent

    @property
    def name(self):
        buf = create_string_buffer(512)
        length = so.REDFont_GetName(self._font, buf, 512)
        return buf[:length-1].decode()

    @property
    def flags(self):
        return so.REDFont_GetFlags(self._font)

    @property
    def weight(self):
        return so.REDFont_GetWeight(self._font)

    def __del__(self):
        so.REDFont_Destroy(self._font)

    def __repr__(self):
        return f'<RED_Font name={self.name}, flags={self.flags:04x}, weight={self.weight}>'

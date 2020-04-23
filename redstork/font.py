import re
from ctypes import create_string_buffer, c_int, pointer
from .bindings import so
from .glyph import Glyph


class Font:
    '''Represents font used in a PDF file.'''

    # Font styles as defined in PDF 1.7 Table 5.20
    FLAGS_NORMAL = 0                #: Normal font
    FLAGS_FIXED_PITCH = (1 << 0)    #: Fixed pitch font
    FLAGS_SERIF = (1 << 1)          #: Serif font
    FLAGS_SYMBOLIC = (1 << 2)       #: Symbolic font
    FLAGS_SCRIPT = (1 << 3)         #: Script font
    FLAGS_NONSYMBOLIC = (1 << 5)    #: Non-symbolic font
    FLAGS_ITALIC = (1 << 6)         #: Italic font
    FLAGS_ALLCAP = (1 << 16)        #: All-cap font
    FLAGS_SMALLCAP = (1 << 17)      #: Small-cap font
    FLAGS_FORCE_BOLD = (1 << 18)    #: Force-bold font

    def __init__(self, font, parent):
        self._font = font
        self._parent = parent

    @property
    def name(self):
        '''Font name in the PDF document.'''
        buf = create_string_buffer(512)
        length = so.REDFont_GetName(self._font, buf, 512)
        return buf[:length].decode()

    @property
    def simple_name(self):
        '''Font name without PDF-specific prefix.'''
        name =self.name
        mtc = re.match(r'(.*?)\+(.*)$', name)
        if mtc is not None:
            return mtc.group(2)
        return name

    @property
    def flags(self):
        '''Font flags.'''
        return so.REDFont_GetFlags(self._font)

    @property
    def weight(self):
        '''Font weight.'''
        return so.REDFont_GetWeight(self._font)

    @property
    def is_vertical(self):
        '''True for vertical writing systems (CJK)'''
        return so.REDFont_IsVertical(self._font) != 0

    @property
    def id(self):
        '''Tuple of (Object_id, Generation_id), identifying underlaying stream in PDF file'''
        obj_id = c_int(0)
        gen_id = c_int(0)

        if not so.REDFont_GetId(self._font, pointer(obj_id), pointer(gen_id)):
            raise RuntimeError('unexpected error: font id not found')

        return obj_id.value, gen_id.value

    def load_glyph(self, charcode):
        '''Load glyph, see :class:`Glyph`

        Args:
            charcode (int): the character code (see :class:`TextObject`)
        '''
        g = so.REDFont_LoadGlyph(self._font, charcode)
        if g is None:
            return None
        return Glyph(g, self._font)

    def __getitem__(self, charcode):
        '''Returns Unicode text of this character.

        Args:
            charcode (int) - the character code (see :class:`TextObject`)
        '''
        buf = create_string_buffer(16)
        length = so.REDFont_UnicodeFromCharCode(self._font, c_int(charcode), buf, 16)
        return buf[:length].decode()

    def __del__(self):
        so.REDFont_Destroy(self._font)

    def __repr__(self):
        return f'<RED_Font name={self.name}, flags={self.flags:04x}, weight={self.weight}>'

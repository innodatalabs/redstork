import re
from ctypes import create_string_buffer, c_int, pointer, cast, c_char_p
from .bindings import so
from .glyph import Glyph
from .unicode_map import UnicodeMap


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
        self._unicode_map = UnicodeMap.NotParsed
        self._text_cache = {}
        self._glyph_cache = {}

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
        if charcode not in self._glyph_cache:
            g = so.REDFont_LoadGlyph(self._font, charcode)
            g = Glyph(g, self._font) if g is not None else None
            self._glyph_cache[charcode] = g
        return self._glyph_cache[charcode]

    def load_unicode_map(self):
        if self._unicode_map is UnicodeMap.NotParsed:
            umap = so.REDFont_LoadUnicodeMap(self._font)
            if umap is None:
                self._unicode_map = None
            else:
                text = cast(umap, c_char_p).value.decode()
                self._unicode_map = UnicodeMap(text)
                so.REDFont_DestroyUnicodeMap(umap)
        return self._unicode_map

    def save_unicode_map(self):
        if not self.changed:
            return
        data = self._unicode_map.format().encode()
        if not so.REDFont_WriteUnicodeMap(self._font, data, len(data)):
            raise RuntimeError('Failed to save unicode map')
        self._unicode_map.sync()

    @property
    def changed(self):
        if self._unicode_map in (None, UnicodeMap.NotParsed):
            return False
        return self._unicode_map.changed

    def __getitem__(self, charcode):
        '''Returns Unicode text of this character.

        Args:
            charcode (int) - the character code (see :class:`TextObject`)
        '''
        umap = self.load_unicode_map()
        if umap is not None:
            text = umap.get(charcode)
            if text is not None:
                return text
        text = self._text_cache.get(charcode)
        if text is None:
            buf = create_string_buffer(16)
            length = so.REDFont_UnicodeFromCharCode(self._font, c_int(charcode), buf, 16)
            text = buf[:length].decode('utf-8', 'surrogatepass')
            self._text_cache[charcode] = text
        return text

    @property
    def is_editable(self):
        '''True if font encoding can be changed'''
        return self.load_unicode_map() is not None

    def __setitem__(self, charcode, text):
        '''Updates font encoding.

        Args:
            charcode (int): character code
            text (str): new text for this character code

        Raises:
            :class:`ReadOnlyEncodingError`: if encoding is read-one (no "ToUnicode" map in the font dictionary)
        '''
        umap = self.load_unicode_map()
        if umap is None:
            raise ReadOnlyEncoding('can not change encoding')
        umap[charcode] = text

    def __del__(self):
        so.REDFont_Destroy(self._font)

    def __repr__(self):
        return f'<RED_Font name={self.name}, flags={self.flags:04x}, weight={self.weight}>'


class ReadOnlyEncodingError(RuntimeError):
    ...
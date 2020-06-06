import re
import itertools
from .dict_changed import DictChanged


class UnicodeMap(DictChanged):
    '''Represents PDF "ToUnicode" optional data structure that controls character encoding'''
    NotParsed = object()  #: for internal use

    def __init__(self, text):
        self._text = text
        super().__init__(_parse(text))

    def format(self):
        '''Generates string representing the PDF stream, ready to be inserted into the PDF file'''
        if not self.changed:
            return self._text

        return _format(self, self._text)


_RE_CODE = r'<([\dA-Fa-f]{2,4})>'
_RE_TEXT = r'<([\dA-Fa-f ]+)>'

def _parse(text):
    umap = {}
    for mtc in re.finditer(r'\s*\d+\sbeginbfchar(.*?)endbfchar\s*', text, flags=re.DOTALL):
        for key, val in _parse_bfchar(mtc.group(1)):
            umap[key] = val
    for mtc in re.finditer(r'\s*\d+\sbeginbfrange(.*?)endbfrange\s*', text, flags=re.DOTALL):
        for key, val in _parse_bfrange(mtc.group(1)):
            umap[key] = val
    return umap

def _parse_bfchar(text):
    text = text.strip()
    if text == '':
        return
    off = 0
    for mtc in re.finditer(_RE_CODE + r'\s*' + _RE_TEXT + r'\s*', text):
        assert mtc.start() == off, text
        off = mtc.end()
        key = int(mtc.group(1), 16)
        val = ''.join(_parse_text(mtc.group(2)))
        yield key, val
    assert off == len(text), text

def _parse_text(text):
    text = text.replace(' ', '')
    if len(text) == 2:
        return chr(int(text, 16))
    tx = []
    for off in range(0, len(text), 4):
        x = text[off:off+4]
        assert len(x) == 4, text
        tx.append(chr(int(x, 16)))
    assert len(tx) >= 1, text
    return tx

def _parse_bfrange(text):
    text = text.strip()
    if text == '':
        return
    for line in text.split('\n'):
        line = line.strip()
        mtc = re.match(_RE_CODE + r'\s*' + _RE_CODE + r'\s*' + _RE_TEXT + r'$', line)
        if mtc is not None:
            yield from _parse_implicit_range(mtc.group(1), mtc.group(2), mtc.group(3))
        else:
            mtc = re.match(_RE_CODE + r'\s*' + _RE_CODE + r'\s*\[(.*)\]$', line)
            assert mtc, text
            yield from _parse_explicit_range(mtc.group(1), mtc.group(2), mtc.group(3))

def _parse_implicit_range(start_code, end_code, start_text):
    start_code = int(start_code, 16)
    end_code   = int(end_code, 16) + 1
    start_text = _parse_text(start_text)

    assert start_code < end_code
    prefix = ''.join(start_text[:-1])
    last_text_ord = ord(start_text[-1])
    for i,code in enumerate(range(start_code, end_code)):
        yield code, prefix + chr(i + last_text_ord)

def _parse_explicit_range(start_code, end_code, text_list):
    start_code = int(start_code, 16)
    end_code   = int(end_code, 16) + 1

    off = 0
    texts = []
    for mtc in re.finditer(_RE_TEXT + r'\s*', text_list):
        assert mtc.start() == off, text_list
        off = mtc.end()
        val = ''.join(_parse_text(mtc.group(1)))
        texts.append(val)
    assert off == len(text_list), text_list
    assert start_code < end_code
    assert len(texts) == end_code - start_code
    yield from zip(range(start_code, end_code), texts)


def _format(mapping, text):
    bfchars, bfranges = _format_mapping(mapping)

    preamble, postamble = _clear_bfchars_bfranges(text)

    text = []
    if preamble:
        text.append(preamble)

    for bfchar in bfchars:
        if bfchar:
            text.append(f'{len(bfchar)} beginbfchar')
            for x, y in bfchar:
                text.append(f'<{_format_hex_code(x)}> <{_format_hex_text(y)}>')
            text.append('endbfchar')

    for bfrange in bfranges:
        if bfrange:
            text.append(f'{len(bfrange)} beginbfrange')
            for x, y, z in bfrange:
                text.append(f'<{_format_hex_code(x)}> <{_format_hex_code(y)}> <{_format_hex_text(z)}>')
            text.append('endbfrange')

    if postamble:
        text.append(postamble)

    return '\n'.join(text)

def _format_mapping(mapping):
    code_groups = []

    # PDF spec state that bfchar can not be longer than 100 items, and can not span codes that have different high-order byte
    for _, codes in itertools.groupby(sorted(mapping.keys()), lambda code: code // 256):
        codes = list(codes)
        for off in range(0, len(codes), 100):
            code_groups.append(codes[off:off+100])

    bfchars = []
    bfgroups = []

    for g in code_groups:
        bfchar, bfrange = _try_compress([ (x, mapping[x]) for x in g ])
        bfchars.append(bfchar)
        bfgroups.append(bfrange)

    # FIXME: generate groups too!
    return bfchars, bfgroups

def _clear_bfchars_bfranges(text):
    mtc = re.search(r'\s*\d+\s+beginbfchar', text)
    if mtc is None:
        mtc = re.search(r'\s*\d+\s+beginbfrange', text)
    assert mtc, text

    preamble = text[:mtc.start()]
    rest = text[mtc.start():]
    rest = re.sub(r'\s*\d+\s+beginbfchar.*?endbfchar\s*', '', rest, flags=re.DOTALL)
    assert not re.search(r'beginbfchar', rest), rest
    rest = re.sub(r'\s*\d+\s+beginbfrange.*?endbfrange\s*', '', rest, flags=re.DOTALL)
    assert not re.search(r'beginbfrange', rest), rest

    return preamble, rest

def _format_hex_code(code):
    text = hex(code)[2:].upper()
    assert len(text) <= 4, (code, hex(code).upper())

    return '0' * (4-len(text)) + text  # leading zeroes, if needed

def _format_hex_text(text):
    if text == '':
        text = ' '

    out = []
    for c in text:
        out.append(_format_hex_code(ord(c)))
    return ''.join(out)

def _sequential_blocks(chars):
    old_code, old_text = chars[0]
    block = [ (old_code, old_text) ]
    for code, text in chars[1:]:
        if old_code+1 != code or not _is_sequential_text(old_text, text):
            yield block[:]
            block.clear()
        block.append((code, text))
        old_code, old_text = code, text
    yield block

def _try_compress(chars):
    bfchars = []
    bfranges = []

    for block in _sequential_blocks(chars):
        if len(block) <= 2:
            bfchars.extend(block)
        else:
            code, text = block[0]
            bfranges.append((code, code+len(block)-1, text))

    return bfchars, bfranges

def _is_sequential_text(text0, text1):
    if len(text0) != len(text1):
        return False
    if text0[:-1] != text1[:-1]:
        return False
    return ord(text0[-1]) +1 == ord(text1[-1])
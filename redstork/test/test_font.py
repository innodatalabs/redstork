from redstork import Document, PageObject
from . import res
import tempfile


def test_font():
    doc = Document(res('sample.pdf'))
    page = doc[2]
    assert len(page) == 19

    text_objs = [x for x in page if x.type == PageObject.OBJ_TYPE_TEXT]
    font = text_objs[0].font

    assert font.name == 'KQFFMA+NimbusSanL-Regu'
    assert font.simple_name == 'NimbusSanL-Regu'
    assert font.id == (53, 0)
    assert font.is_vertical is False


def test_glyph():
    doc = Document(res('sample.pdf'))
    page = doc[2]
    assert len(page) == 19

    text_objs = [x for x in page if x.type == PageObject.OBJ_TYPE_TEXT]
    font = text_objs[0].font

    chars = list(text_objs[0])
    assert len(chars) == 8

    assert chars[0][0] == 77
    assert font[chars[0][0]] == 'M'
    glyph = font.load_glyph(77)
    assert glyph is not None
    assert len(glyph) == 14
    assert list(glyph) == [
        (0.468017578125, 0.0, 2, False),
        (0.673095703125, 0.611083984375, 0, False),
        (0.673095703125, 0.0, 0, False),
        (0.760986328125, 0.0, 0, False),
        (0.760986328125, 0.72900390625, 0, False),
        (0.632080078125, 0.72900390625, 0, False),
        (0.419921875, 0.093994140625, 0, False),
        (0.2041015625, 0.72900390625, 0, False),
        (0.074951171875, 0.72900390625, 0, False),
        (0.074951171875, 0.0, 0, False),
        (0.1630859375, 0.0, 0, False),
        (0.1630859375, 0.611083984375, 0, False),
        (0.3701171875, 0.0, 0, False),
        (0.468017578125, 0.0, 0, True),
    ]


def test_scaling():
    doc = Document(res('sample.pdf'))

    SCALE = 4 * 1024
    for page in doc:
        text_objs = [x for x in page if x.type == PageObject.OBJ_TYPE_TEXT]
        for text_obj in text_objs:
            font = text_obj.font

            for code, _, _ in text_obj:
                glyph = font.load_glyph(code)

            for x, y, typ, close in glyph:
                xscaled = SCALE * x
                yscaled = y * SCALE
                assert xscaled == int(xscaled)
                assert yscaled == int(yscaled)

def test_document_fonts():
    doc = Document(res('sample.pdf'))

    for page in doc:
        list(page)  # forces reading of the page objects and populates fonts

    assert len(doc.fonts) == 9

    names = [x.simple_name for x in doc.fonts.values()]
    assert names == [
        'NimbusSanL-Bold',
        'NimbusSanL-BoldItal',
        'NimbusSanL-Regu',
        'NimbusRomNo9L-Medi',
        'NimbusRomNo9L-Regu',
        'NimbusMonL-Bold',
        'NimbusMonL-Regu',
        'NimbusRomNo9L-ReguItal',
        'NimbusMonL-ReguObli',
    ]


def test_unicode_map():
    doc = Document(res('tt2.pdf'))

    list(doc[1])  # read all objects from page 2. This populates doc.fonts
    font = doc.fonts[33, 0]
    assert font.is_editable
    assert font[30] == '\u037e'

    font[30] = ';'
    assert font.changed
    assert font[30] == ';'

    with tempfile.TemporaryDirectory() as d:
        fname = f'{d}/temp.pdf'
        doc.save(fname)

        doc = Document(fname)
        list(doc[1])  # read all objects from page 2. This populates doc.fonts
        font = doc.fonts[33, 0]
        assert font.is_editable
        assert font[30] == ';'

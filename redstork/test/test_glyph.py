from redstork import Document, PageObject
from . import res


def test_glyph():

    doc = Document(res('arxiv1901.10092.pdf'))
    page = doc[0]

    glyphs = []
    for o in page.flat_iter():
        if o.type == PageObject.OBJ_TYPE_TEXT:
            font = o.font
            for c, _, _ in o:
                if c != -1:
                    glyph = font.load_glyph(c)
                    glyphs.append(glyph)

    assert len(glyphs) == 5699
    glyph = glyphs[1000]
    assert glyph.bounds() == (0.009033203125, -0.010986328125, 0.696044921875, 0.43701171875)
    assert glyph.ascent == 0.43701171875
    assert glyph.descent == 0.010986328125
    assert glyph.advance == 0.696044921875

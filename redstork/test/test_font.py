from redstork import Document, PageObject
from . import res


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

from redstork import Document, PageObject
from . import res


def test_page_object_smoke():
    doc = Document(res('sample.pdf'))
    page = doc[2]
    assert len(page) == 19

    text_objs = [x for x in page if x.type == PageObject.OBJ_TYPE_TEXT]
    path_objs = [x for x in page if x.type == PageObject.OBJ_TYPE_PATH]
    assert len(text_objs) == 16
    assert len(path_objs) == 3


def test_page_object_chars():
    doc = Document(res('sample.pdf'))
    page = doc[2]
    assert len(page) == 19

    text_objs = [x for x in page if x.type == PageObject.OBJ_TYPE_TEXT]
    text = text_objs[0]
    assert len(text) == 8

    items = list(text)

    assert items == [
        (77, 0.0, 0.0),
        (97, 11.950385093688965, 0.0),
        (110, 19.92687225341797, 0.0),
        (-1, 10.0, 0.0),
        (117, 27.759897232055664, 0.0),
        (97, 35.736385345458984, 0.0),
        (108, 43.71287155151367, 0.0),
        (58, 46.897727966308594, 0.0),
    ]

    assert text.text == 'Manual:'

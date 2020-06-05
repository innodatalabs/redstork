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

def test_text_geometry_iter():
    doc = Document(res('sample.pdf'))
    page = doc[2]
    assert len(page) == 19

    text_objs = [
        x for x in page.flat_iter()
        if x.type == PageObject.OBJ_TYPE_TEXT
    ]
    text = text_objs[0]
    assert len(text) == 8

    items = list(text.text_geometry_iter())
    assert items == [
        ('M', (489.1150207519531, 619.3770141601562, 500.0322828043718, 629.8354499922134)),
        ('a', (660.5576352553899, 619.0477800783701, 668.231591353192, 627.1105125918984)),
        ('n', (774.989915261096, 619.3770141601562, 781.9773832734718, 627.1105125918984)),
        ('u', (887.3640581259624, 619.0477800783701, 894.277973843471, 626.8933581975289)),
        ('a', (1001.796351813271, 619.0477800783701, 1009.4703079110732, 627.1105125918984)),
        ('l', (1116.2286181373747, 619.3770141601562, 1118.4106695517657, 629.8354499922134)),
        (':', (1161.9192052012877, 619.3770141601562, 1164.9908891345476, 626.8933581975289)),
    ]

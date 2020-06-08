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
        ('a', (501.0654058456421, 619.0477800783701, 508.73936194344424, 627.1105125918984)),
        ('n', (509.0418930053711, 619.3770141601562, 516.0293610177469, 627.1105125918984)),
        ('u', (516.8749179840088, 619.0477800783701, 523.7888337015174, 626.8933581975289)),
        ('a', (524.8514060974121, 619.0477800783701, 532.5253621952143, 627.1105125918984)),
        ('l', (532.8278923034668, 619.3770141601562, 535.0099437178578, 629.8354499922134)),
        (':', (536.0127487182617, 619.3770141601562, 539.0844326515216, 626.8933581975289)),
    ]

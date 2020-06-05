from redstork import Document, PageObject
from redstork.test import res


def test_page_smoke():

    doc = Document(res('sample.pdf'))

    page = doc[0]

    assert page.media_box == (0., 0., 612., 792.)
    assert page.crop_box == (0., 0., 612., 792.)


def test_page_label():
    doc = Document(res('sample.pdf'))

    assert doc[2].label == 'i'
    assert doc[-3].label == '9'

def test_flatiter():
    '''used to crash'''
    doc = Document(res('arxiv1901.10092.pdf'))

    text = []
    for obj in doc[0].flat_iter():
        if obj.type == PageObject.OBJ_TYPE_TEXT:
            text.append(obj.text)  # should not crash
    assert ''.join(text)[-20:] == 're.com/naturephysics'

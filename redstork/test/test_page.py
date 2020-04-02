from redstork import Document
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

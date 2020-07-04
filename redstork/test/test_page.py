from redstork import Document, PageObject, Page
from redstork.pageobject import apply
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

def test_get_fsmatrix():
    crop_box = (0, 0, 100, 200)
    rect = (5, 100, 55, 150)

    # rotation=0
    matrix = Page._get_fsmatrix(0, crop_box, rect, 1)
    matrix = (matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f)
    assert matrix == (1, 0, 0, 1, -5, -50)
    assert apply(matrix, (5, 50)) == (0, 0)  # top left corner
    assert apply(matrix, (5, 100)) == (0, 50)  # bottom left corner
    assert apply(matrix, (55, 50)) == (50, 0)  # top right corner
    assert apply(matrix, (55, 100)) == (50, 50)  # bottom right corner

    # TODO: test other rotations (need a PDF sample)
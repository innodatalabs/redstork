from redstork import Document, PageObject
from . import res


def inside(page, box, coverage=0.90):
    px0, py0, px1, py1 = page
    x0, y0, x1, y1 = box

    area = (x1 - x0) * (y1 - y0)

    x0 = max(x0, px0)
    x1 = min(x1, px1)
    y0 = max(y0, py0)
    y1 = min(y1, py1)

    cover = (x1 - x0) * (y1 - y0)
    return cover / (area + 1.e-8) > coverage


def test_rotated_text():
    doc = Document(res('arxiv1901.02066.pdf'))

    page = doc[0]
    objs = list(page.flat_iter())
    obj = objs[296]
    rect = obj.rect
    text_geom = list(obj.text_geometry_iter())
    assert all(inside(rect, bx) for _,bx in text_geom)

def test_geometry_sane():

    for fname in [
        'arxiv1901.01387.pdf',
        'arxiv1901.02668.pdf',
        'arxiv1901.09059.pdf',
        'arxiv1901.02066.pdf',
        'arxiv1901.08145v1.pdf',
        'arxiv1901.10092.pdf',
        # 'arxiv1901.02527.pdf',
        # 'arxiv1901.08637.pdf',
        'arxiv1901.11067.pdf'
    ]:
        doc = Document(res(fname))

        for pageidx,page in enumerate(doc):
            objcount = 0
            for obj in page.flat_iter():
                if obj.type == PageObject.OBJ_TYPE_TEXT:
                    txt_boxes = list(obj.text_geometry_iter())
                    for _,bx in txt_boxes:
                        assert inside(page.crop_box, bx), (fname, pageidx, page.crop_box, objcount, bx)
                    # assert all(inside(obj.rect, bx) for _,bx in txt_boxes), (fname, pageidx, obj.rect, objcount)
                objcount += 1

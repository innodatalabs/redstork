from redstork import Document, Page
from . import res
import os

def test_page_label():
    doc = Document(res('sample.pdf'))
    page = doc[2]
    assert len(page) == 19

    text_objs = [x for x in page if x.type == Page.OBJ_TYPE_TEXT]
    path_objs = [x for x in page if x.type == Page.OBJ_TYPE_PATH]
    assert len(text_objs) == 16
    assert len(path_objs) == 3

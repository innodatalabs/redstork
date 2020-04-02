from redstork import Document
from redstork.test import res


def test_document():
    doc = Document(res('sample.pdf'))

    assert len(doc) == 15

    assert doc.meta['Title'] == 'Red Stork'
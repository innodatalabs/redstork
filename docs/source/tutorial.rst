Tutorial
========

.. module:: redstork
    :noindex:
.. Red Stork tutorial

The philosophy of **redstork** is to map API to standard and well undersood Python objects, like
:class:`list` and :class:`dict`.

In this tutorial we will use the following :download:`sample document <../../redstork/test/resources/sample.pdf>`.

Version
-------

There are two version values in :mod:`redstork` module: PDFium build version, and Python package version::

    import redstork

    redstork.__pdfium_version__
    >> 'cromium/4097'

    redstork.__version__
    >> '0.0.1'

Document
--------

:class:`Document` is the top-level object, and the only object that can be instantiated directly::

    from redstork import Document

    doc = Document('sample.pdf')

    len(doc)
    >> 15

As you can see, :class:`Document` resembles standard Python :class:`list`, containing :class:`Page` objects.

PDF file creators can attach arbitraty key-value strings to the document, that we call ``meta`` (official
PDf specs call it ``Document Information Dictionary``).
Most commonly these values describe ``Author``, ``Title``, and the name of software that created this
document. Lets see the meta in our sample::

    doc.meta['Title']
    >> 'Red Stork'

Page
----

:class:`Page` represents PDF page. Get page by indexing a :class:`Document` object, just like a normal list::

    page = doc[0]
    page.crop_box
    >> (0.0, 0.0, 612.0, 792.0)

:class:`Page` has :attr:`Page.label`, representing the page label (like ``xxi``, or ``128``)::

    doc[2].label  # this is the label of the third page
    >> 'i'

.. To be continued ..
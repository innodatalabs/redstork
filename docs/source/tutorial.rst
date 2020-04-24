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

You can change `meta` content and save the updated document::

    doc.meta['Title'] = 'Awesome PDF parsing library'
    doc.save('awesome.pdf')

Document has a lazily populated collection of fonts. Initially this collection is empty. As pages are being accessed
and parsed, this collection is being populated::

    list(doc[0])  # read all objects from page 1
    len(doc.fonts)
    >> 2


Page
----

:class:`Page` represents PDF page. Get page by indexing a :class:`Document` object, just like a normal list::

    page = doc[0]
    page.crop_box
    >> (0.0, 0.0, 612.0, 792.0)

:class:`Page` has :attr:`Page.label`, representing the page label (like ``xxi``, or ``128``)::

    doc[2].label  # this is the label of the third page
    >> 'i'

A page of PDF document is a list-like object, containing concrete instances of :class:`PageObject`::

    page = ...
    len(page)  # how many objects on this page?
    >> 17


PageObject
----------

Abstract class :class:`PageObject` describes an object on a PDF page. Concrete classes implementing `PageObject` are:

* :class:`TextObject` - a string of characters
* :class:`PathObject` - vector graphics
* :class:`ImageObject` - a bitmap image
* :class:`ShadingObject` - a shading object

Notable properties of all objects are:

* :meth:`PageObject.page` - links back to the parent page
* :meth:`PageObject.matrix` - transformation matrix of this object
* :meth:`PageObject.rect` - rectangle of this object on the page


TextObject
----------

Text object represents a string of characters. Each character is a three-tuple of `(charcode, x, y)`, where
`charcode` is a character code (this value is just an index in the font glyph table, not a
text corresponding to this character!). `x` and `y` are placement coordinates of this character (in the
coordinate system of this `TextObject` - first character typically has `x,y == 0, 0`.

Text object has font property. Here is how to use font to extract text of a `TextObject`::

    def text_of(o):
        assert o.type == PageObject.OBJ_TYPE_TEXT, o
        text = []
        for c, x, y in o:
            text.append(o.font[c])
        return '.join(text)

    page = ...
    for o in page:
        if o.type == PageObject.OBJ_TYPE_TEXT:
            text = text_of(o)
            print(text)


PathObject
----------

Path object represents a set of vector drawing instructions.


ImageObject
-----------

Image object represents an embedded bitmap image. You can ge the pixel width and height of the image, using the properties
:meth:`ImageObject.pixel_width` and :meth:`ImageObject.pixel_height`.

Example::

    page = ...
    for o in page:
        if o.type == PageObject.OBJ_TYPE_IMAGE:
            print(o.pixel_width, o.pixel_height)


Font
----

Font object is a look-up table for character text, and also holds character glyphs (shape).

Font names in PDF file have a special prefix. To get a human-friendly one use :meth:`Font.short_name`.

Document contains a lazy font collection :meth:`Document.fonts`. It is lazy, because just after document is opened,
it is empty. As pages are accessed and parsed, this collection is populated.

Here is how to get :class:`Glyph` object::

    page = ...
    for o in page:
        if o.type == PageObject.OBJ_TYPE_TEXT:
            for code,_,_ in o:
                glyph = o.font.load_glyph(code)
                print('Character with code %d has %d glyph instructions', code, len(glyph))


.. To be continued ..
Red Stork
=========

Yet another PDF parser. This one is based on PDFium_ engine.

.. _PDFium: https://pdfium.googlesource.com/pdfium/


Quick Start
^^^^^^^^^^^

Sample::

    from redstork.document import Document

    doc = Document('sample.pdf')
    print('Number of pages:', len(doc))


.. toctree::
    :maxdepth: 2
    :caption: Manual:

    tutorial.rst
    reference.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`

Red Stork
=========

Yet another PDF parser. This one is based on PDFium_ engine.

.. _PDFium: https://pdfium.googlesource.com/pdfium/


Quick Start
^^^^^^^^^^^

Sample::

    from redstork import PDF_Document

    doc = PDF_Document('sample.pdf')
    print('Number of pages:', len(doc))


.. toctree::
    :maxdepth: 2
    :caption: Red Stork manual:

    tutorial.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`

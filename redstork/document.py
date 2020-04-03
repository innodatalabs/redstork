import os
from ctypes import create_string_buffer
from .page import Page
from .bindings import so


class Document:
    '''PDF document.

    A :class:`list`-like container of pages. Sample use::

        doc = Document('sample.pdf')
        print("Number of pages:', len(doc))

        for key, value in doc.meta.items():
            print('\t', key, ':', value)
    '''

    def __init__(self, file_name, password=None):
        '''Create new PDF Document object, from a file.

        Args:
            file_name (str): Name of PDF file
            password (str):  File password (optional)
        '''
        self._doc = None
        c_fname = create_string_buffer(file_name.encode() + b'\0')
        c_password = create_string_buffer(password.encode() + b'\0') if password is not None else None

        self.file_name = file_name
        self._doc = so.RED_LoadDocument(c_fname, c_password)
        if self._doc is None:
            raise RuntimeError('Failed to open document: %s' % file_name)
        self.numpages = so.FPDF_GetPageCount(self._doc) #: :class:`int` -- total number of pages
        self.meta = self._get_meta_dict(self._doc)      #: :class:`dict` -- document meta info (Author, Title, etc)

    def __del__(self):
        if self._doc is not None:
            so.FPDF_CloseDocument(self._doc)

    def __getitem__(self, page_index):
        '''Returns :class:`Page` at this index.

        Example::

            doc = ...

            page = doc[0]  # first page

        Args:
            page_index (int): zero-based page index
        Returns:
            :class:`Page` object
        '''
        if page_index < 0:
            page_index = self.numpages + page_index
        if 0 <= page_index < self.numpages:
            return Page(so.FPDF_LoadPage(self._doc, page_index), page_index, self)
        raise ValueError('Page number %s is out of range: 0..%s' % (page_index, self.numpages))

    def __len__(self):
        '''Returns number of pages in this document'''
        return self.numpages

    def __iter__(self):
        '''Iterate over the pages of this document'''
        for i in range(len(self)):
            yield self[i]

    def _get_page_label(self, page_index):
        out = create_string_buffer(4096)
        l = so.FPDF_GetPageLabel(self._doc, page_index, out, 4096)
        return out.raw[:l-2].decode('utf-16le')

    @classmethod
    def _get_meta_dict(cls, doc):
        out = {}
        num_keys = so.REDDoc_GetMetaTextKeyCount(doc)
        for i in range(num_keys):
            key = so.REDDoc_GetMetaTextKeyAt(doc, i)
            if key is None:
                continue
            key = key.decode()
            value = cls._get_meta_text(doc, key)
            out[key] = value
        return out

    @classmethod
    def _get_meta_text(cls, doc, key):
        out = create_string_buffer(512)
        l = so.FPDF_GetMetaText(doc, create_string_buffer(key.encode() + b'\0'), out, 512)
        return out.raw[:l-2].decode('utf-16le')

    def __repr__(self):
        return f'<Document fname={self.fname}, numpages={self.numpages}>'

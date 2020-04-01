import red

if __name__ == '__main__':
    import os

    fname = os.path.expanduser('~/REDSync/testResources/izguts/9783642051104.pdf')

    doc = red.RED_Document(fname)
    for key, val in doc.meta.items():
        print(key, val)

    print(doc.numpages)
    for page_index in range(doc.numpages):
        print('Page:', page_index)
        page = doc[page_index]
        print(page, page.width, page.height, page.bbox, page.crop_box, page.media_box, page.label, page.rotation, len(page))
        for x in page:
            print(x.rect, x.type, x)
            if x.type == red.page.RED_Page.OBJ_TYPE_TEXT:
                print('\t', x.font)
                page.render('first_text.ppm', scale=5, rect=x.rect)
                assert False
        break

    doc[0].render_('test_000_.ppm')
    doc[1].render_('test_001_.ppm')
    doc[2].render_('test_002_.ppm')
    doc[3].render_('test_003_.ppm')

    doc[0].render('test_000.ppm')
    doc[1].render('test_001.ppm')
    doc[2].render('test_002.ppm')
    doc[3].render('test_003.ppm')


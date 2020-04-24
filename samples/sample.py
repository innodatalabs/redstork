from redstork import Document, PageObject, Glyph
from redstork.test import res

doc = Document(res('sample.pdf'))

print('Number of pages:', len(doc))

print('MediaBox of the first page is:', doc[0].media_box)

print('Rotation of the first page is:', doc[0].rotation)

print('Document title:', doc.meta['Title'])

print('First page has', len(doc[0]), 'objects')

doc[0].render('page-0.ppm', scale=2)   # render page #1 as image

page = doc[0]
for o in page:
    if o.type == PageObject.OBJ_TYPE_TEXT:
        for code, _, _ in o:
            print(o.font[code], end='')
        print()

for fid, font in doc.fonts.items():
    print(font.simple_name, fid)

# lets generate an SVG file of the first letter on page 1
text_object = [o for o in page if o.type == PageObject.OBJ_TYPE_TEXT][0]  # first text object
charcode, _, _ = text_object[0]  # first character of the first text object

glyph = font.load_glyph(charcode)
path, delayed_c = [], []
for x, y, op, close in glyph:
    x, y = round(x, 3), round(y, 3)
    if op == Glyph.MOVETO:
        path.append(f'M {x} {y}')
    elif op == Glyph.LINETO:
        path.append(f'L {x} {y}')
    elif op == Glyph.CURVETO:
        delayed_c.append(f'{x} {y}')
        if len(delayed_c) == 3:
            path.append('C ' + ', '.join(delayed_c))
            delayed_c.clear()
    if close:
        path.append('Z')
path = ' '.join(path)
print('<svg><g fill="gray" transform="scale(100,-100)"><path d="' + path + '" /></g></svg>')

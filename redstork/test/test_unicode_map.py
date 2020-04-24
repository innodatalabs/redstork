from redstork.unicode_map import UnicodeMap

def test_unicode_map():
    stream = '''\
/CIDInit /ProcSet findresource begin
12 dict begin
begincmap
/CIDSystemInfo
<<  /Registry (Adobe)
/Ordering (UCS)
/Supplement 0
>> def
/CMapName /Adobe-Identity-UCS def
/CMapType 2 def
1 begincodespacerange
<0001> <0D5C>
endcodespacerange
15 beginbfchar
<0003> <00A0>
<000F> <002C>
<0010> <00AD>
<0011> <002E>
<001E> <037E>
<0040> <005D>
<0062> <00C4>
<0067> <00D6>
<0068> <00DC>
<006C> <00E4>
<007C> <00F6>
<0081> <00FC>
<00A9> <00AB>
<00AA> <00BB>
<00AB> <2026>
endbfchar
5 beginbfrange
<000B> <000C> <0028>
<0013> <001D> <0030>
<0024> <003A> <0041>
<003D> <003E> <005A>
<0044> <005D> <0061>
endbfrange
endcmap
CMapName currentdict /CMap defineresource pop
end
end\
'''
    umap = UnicodeMap(stream)
    assert len(umap) == 79

    umap[0x1e] = ';'
    assert len(umap) == 79
    assert umap.changed

    model = '''\
/CIDInit /ProcSet findresource begin
12 dict begin
begincmap
/CIDSystemInfo
<<  /Registry (Adobe)
/Ordering (UCS)
/Supplement 0
>> def
/CMapName /Adobe-Identity-UCS def
/CMapType 2 def
1 begincodespacerange
<0001> <0D5C>
endcodespacerange
18 beginbfchar
<0003> <00A0>
<000B> <0028>
<000C> <0029>
<000F> <002C>
<0010> <00AD>
<0011> <002E>
<003D> <005A>
<003E> <005B>
<0040> <005D>
<0062> <00C4>
<0067> <00D6>
<0068> <00DC>
<006C> <00E4>
<007C> <00F6>
<0081> <00FC>
<00A9> <00AB>
<00AA> <00BB>
<00AB> <2026>
endbfchar
3 beginbfrange
<0013> <001E> <0030>
<0024> <003A> <0041>
<0044> <005D> <0061>
endbfrange
endcmap
CMapName currentdict /CMap defineresource pop
end
end\
'''
    result = umap.format()
    if result != model:
        print(model.encode())
        print(result.encode())
        print(result)
        assert False

    result2 = UnicodeMap(result).format()
    assert result2 == result

def test_unicode_map_02():

    umap = UnicodeMap('''\
1 beginbfchar
<0001> <0001>
<0002> <0002>
<0101> <0101>
<0102> <0102>
endbfchar\
''')
    assert dict(umap.items()) == {
        1  : '\x01',
        2  : '\x02',
        257: '\u0101',
        258: '\u0102',
    }
    umap[3] = '\x03'
    model = '''\
2 beginbfchar
<0101> <0101>
<0102> <0102>
endbfchar
1 beginbfrange
<0001> <0003> <0001>
endbfrange\
'''
    result = umap.format()
    if result != model:
        print(model.encode())
        print(result.encode())
        print(result)
        assert False


def test_unicode_map_03():

    umap = UnicodeMap('''\
1 beginbfchar
<0001> <000100020003>
<0002> <0002>
<0101> <0101>
<0102> <0102>
endbfchar\
''')
    assert dict(umap.items()) == {
        1  : '\x01\x02\x03',
        2  : '\x02',
        257: '\u0101',
        258: '\u0102',
    }
    umap[3] = '\x03'
    model = '''\
3 beginbfchar
<0001> <000100020003>
<0002> <00480065006C006C006F>
<0003> <0003>
endbfchar
2 beginbfchar
<0101> <0101>
<0102> <0102>
endbfchar\
'''
    umap[2] = 'Hello'
    result = umap.format()
    if result != model:
        print(model.encode())
        print(result.encode())
        print(result)
        assert False

from redstork.dict_changed import DictChanged


def test_dict_changed():

    dc = DictChanged(one=1, two=2)
    assert not dc.changed
    assert list(dc.deleted_keys()) == []
    assert list(dc.inserted_keys()) == []
    assert list(dc.updated_keys()) == []

    dc['one'] = 3
    assert dc.changed
    assert list(dc.deleted_keys()) == []
    assert list(dc.inserted_keys()) == []
    assert list(dc.updated_keys()) == ['one']

    dc['one'] = 1
    assert not dc.changed
    assert list(dc.deleted_keys()) == []
    assert list(dc.inserted_keys()) == []
    assert list(dc.updated_keys()) == []

    dc['three'] = 3
    assert dc.changed
    assert list(dc.deleted_keys()) == []
    assert list(dc.inserted_keys()) == ['three']
    assert list(dc.updated_keys()) == []

    del dc['three']
    assert not dc.changed
    assert list(dc.deleted_keys()) == []
    assert list(dc.inserted_keys()) == []
    assert list(dc.updated_keys()) == []

    del dc['one']
    assert dc.changed
    assert list(dc.deleted_keys()) == ['one']
    assert list(dc.inserted_keys()) == []
    assert list(dc.updated_keys()) == []

    dc['one'] = 1
    assert not dc.changed
    assert list(dc.deleted_keys()) == []
    assert list(dc.inserted_keys()) == []
    assert list(dc.updated_keys()) == []

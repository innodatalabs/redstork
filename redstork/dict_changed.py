

class DictChanged(dict):
    '''Dictionary that "knows" if it was changed since creation (or since the latest sync() call)'''
    def __init__(self, *av, **kaw):
        super().__init__(*av, **kaw)
        self._original = dict(self)

    @property
    def changed(self):
        '''Returns True is dictionary content was changed'''
        original_keys = self._original.keys()
        keys = self.keys()
        if original_keys != keys:
            return True
        for key in original_keys:
            if self[key] != self._original[key]:
                return True
        return False

    def sync(self):
        '''Made current state of the dict the golden one'''
        self._original = dict(self)

    def deleted_keys(self):
        '''Returns deleted keys'''
        original_keys = self._original.keys()
        keys = self.keys()
        yield from (original_keys - keys)

    def inserted_keys(self):
        '''Returns inserted keys'''
        original_keys = self._original.keys()
        keys = self.keys()
        yield from (keys - original_keys)

    def updated_keys(self):
        '''Returns updated keys'''
        original_keys = self._original.keys()
        keys = self.keys()
        for key in keys & original_keys:
            if self[key] != self._original[key]:
                yield key

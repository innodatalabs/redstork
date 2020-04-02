import os

def res(*av):
    return os.path.join(os.path.dirname(__file__), 'resources', *av)

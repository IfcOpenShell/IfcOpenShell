import ifcopenshell

class IfcFile(object):
    file = None
    bookmarks = {}

    @classmethod
    def load(cls, path=None):
        cls.file = ifcopenshell.open(path)

    @classmethod
    def get(cls):
        if not cls.file:
            assert False, 'No file was loaded, so this requirement cannot be checked'
        return cls.file

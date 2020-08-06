import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.element

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

    @classmethod
    def by_guid(cls, guid):
        try:
            return cls.get().by_guid(guid)
        except:
            assert False, 'An element with the ID {} could not be found.'.format(guid)

def assert_number(number):
    try:
        return float(number)
    except ValueError:
        assert False, 'A number should be specified, not {}'.format(number)

def assert_type(element, ifc_class, is_exact = False):
    if is_exact:
        assert element.is_a() == ifc_class, 'The element {} is an {} instead of {}.'.format(element, element.is_a(), ifc_class)
    else:
        assert element.is_a(ifc_class), 'The element {} is an {} instead of {}.'.format(element, element.is_a(), ifc_class)

def assert_attribute(element, name, value=None):
    if not hasattr(element, name):
        assert False, 'The element {} does not have the attribute {}'.format(element, name)
    if not value:
        if getattr(element, name) is None:
            assert False, 'The element {} does not have a value for the attribute {}'.format(element, name)
        return
    if value == 'NULL':
        value = None
    actual_value = getattr(element, name)
    if isinstance(value, list):
        actual_value = list(actual_value)
    assert actual_value == value, 'We expected a value of "{}" but instead got "{}" for the element {}'.format(value, actual_value, element)

def assert_pset(element, pset_name, prop_name=None, value=None):
    if value == 'NULL':
        value = None
    psets = ifcopenshell.util.element.get_psets(site)
    if pset_name not in psets:
        assert False, 'The element {} does not have a property set named {}'.format(element, pset_name)
    if prop_name is None:
        return psets[pset_name]
    if prop_name not in psets[pset_name]:
        assert False, 'The element {} does not have a property named "{}" in the pset "{}"'.format(element, prop_name, pset_name)
    if value is None:
        return psets[pset_name][prop_name]
    actual_value = psets[pset_name][prop_name]
    assert actual_value == value, 'We expected a value of "{}" but instead got "{}" for the element {}'.format(value, actual_value, element)

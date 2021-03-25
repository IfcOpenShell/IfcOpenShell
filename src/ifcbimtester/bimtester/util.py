import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.validate
import json
from bimtester.lang import _


def by_types(ifc, ifc_types):
    elements = []
    for ifc_type in ifc_types.split(","):
        elements += ifc.by_type(ifc_type.strip())
    return elements


def validate(ifc):
    errors = []
    logger = ifcopenshell.validate.json_logger()
    try:
        ifcopenshell.validate.validate(ifc, logger)
        if logger.statements:
            for statement in logger.statements:
                errors.append(f"{json.dumps(statement, default=str)}")
    except RuntimeError as error:
        assert False, str(error)


def assert_guid(ifc, guid):
    try:
        return ifc.by_guid(guid)
    except:
        assert False, _("An element with the ID {} could not be found.").format(guid)


def assert_number(number):
    try:
        return float(number)
    except ValueError:
        assert False, _("A number should be specified, not {}").format(number)


def assert_type(element, ifc_class, is_exact=False):
    if is_exact:
        assert element.is_a() == ifc_class, _("The element {} is an {} instead of {}.").format(
            element, element.is_a(), ifc_class
        )
    else:
        assert element.is_a(ifc_class), _("The element {} is an {} instead of {}.").format(
            element, element.is_a(), ifc_class
        )


def assert_attribute(element, name, value=None):
    if not hasattr(element, name):
        assert False, _("The element {} does not have the attribute {}").format(element, name)
    if not value:
        if getattr(element, name) is None:
            assert False, _("The element {} does not have a value for the attribute {}").format(element, name)
        return getattr(element, name)
    if value == "NULL":
        value = None
    actual_value = getattr(element, name)
    if isinstance(value, list) and actual_value:
        actual_value = list(actual_value)
    assert actual_value == value, _('We expected a value of "{}" but instead got "{}" for the element {}').format(
        value, actual_value, element
    )


def assert_pset(element, pset_name, prop_name=None, value=None):
    if value == "NULL":
        value = None
    psets = ifcopenshell.util.element.get_psets(site)
    if pset_name not in psets:
        assert False, _("The element {} does not have a property set named {}").format(element, pset_name)
    if prop_name is None:
        return psets[pset_name]
    if prop_name not in psets[pset_name]:
        assert False, _('The element {} does not have a property named "{}" in the pset "{}"').format(
            element, prop_name, pset_name
        )
    if value is None:
        return psets[pset_name][prop_name]
    actual_value = psets[pset_name][prop_name]
    assert actual_value == value, _('We expected a value of "{}" but instead got "{}" for the element {}').format(
        value, actual_value, element
    )


# TODO: what is this?
def assert_elements(
    ifc_class,
    elemcount,
    falsecount,
    falseelems,
    message_all_falseelems,
    message_some_falseelems,
    message_no_elems,
    parameter=None,
):
    if elemcount > 0 and falsecount == 0:
        return  # Test OK
    elif elemcount == 0:
        assert False, message_no_elems.format(ifc_class=ifc_class)
    elif falsecount == elemcount:
        if parameter is None:
            assert False, message_all_falseelems.format(elemcount=elemcount, ifc_class=ifc_class)
        else:
            assert False, message_all_falseelems.format(elemcount=elemcount, ifc_class=ifc_class, parameter=parameter)
    elif falsecount > 0 and falsecount < elemcount:
        if parameter is None:
            assert False, message_some_falseelems.format(
                falsecount=falsecount,
                elemcount=elemcount,
                ifc_class=ifc_class,
                falseelems=falseelems,
            )
        else:
            assert False, message_some_falseelems.format(
                falsecount=falsecount,
                elemcount=elemcount,
                ifc_class=ifc_class,
                falseelems=falseelems,
                parameter=parameter,
            )
    else:
        assert False, _("Error in falsecount, something went wrong.")

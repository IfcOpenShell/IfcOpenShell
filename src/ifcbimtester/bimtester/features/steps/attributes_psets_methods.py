import gettext  # noqa

from utils import assert_elements
from utils import IfcFile


def all_eleclass_elements_have_prop_in_pset(context, ifc_class, aproperty, pset):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}
    from ifcopenshell.util.element import get_psets

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        psets = get_psets(elem)
        if not (pset in psets and aproperty in psets[pset]):
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
        context.falseprops[elem.id()] = str(psets)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing the property {parameter} in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing the property {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=aproperty
    )
    # the pset name is missing in the failing message, but it is in the step test name

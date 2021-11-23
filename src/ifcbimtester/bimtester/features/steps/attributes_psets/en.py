from behave import step
from behave import use_step_matcher

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('All "{ifc_class}" elements have an "{aproperty}" property in the "{pset}" pset')
def step_impl(context, ifc_class, aproperty, pset):
    eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


# ------------------------------------------------------------------------
# STEPS with Regular Expression Matcher ("re")
# ------------------------------------------------------------------------
use_step_matcher("re")


@step(r"All (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property")
def step_impl(context, ifc_class, property_path):
    import re
    pset, aproperty = property_path.split(".")
    eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step(r'All (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property value matching the pattern "(?P<pattern>.*)"'
)
def step_impl(context, ifc_class, property_path, pattern):
    import re
    from ifcopenshell.util.element import get_psets

    pset_name, property_name = property_path.split(".")
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:

        psets = get_psets(element)

        if  not pset_name in psets:
            assert False
        
        pset = psets[pset_name]
        if not property_name in pset:
            assert False
        
        prop = pset[property_name]
        # get_psets returns just strings

        if not re.search(pattern, prop):
            assert False


def eleclass_has_property_in_pset(
    context, ifc_class, aproperty, pset
):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}
    from ifcopenshell.util.element import get_psets

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        psets = get_psets(elem)
        if not (pset in psets and aproperty in psets[pset]):
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
        context.falseprops[elem.id()] = str(psets)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        # TODO: Translate these messages into other languages
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing the property {parameter} in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing the property {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=aproperty
    )
    # the pset name is missing in the failing message, but it is in the step test name

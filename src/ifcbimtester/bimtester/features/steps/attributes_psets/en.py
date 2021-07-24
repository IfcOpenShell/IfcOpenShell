from behave import step, use_step_matcher

from bimtester.ifc import IfcStore
from bimtester.util import assert_elements
from bimtester.lang import _


@step("all {ifc_class} elements have an {aproperty} property in the {pset} pset")
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


@step(r"all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property")
def step_impl(context, ifc_class, property_path):
    pset_name, property_name = property_path.split(".")
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        if not IfcStore.file.get_property(element, pset_name, property_name):
            assert False


@step(
    r'all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property value matching the pattern "(?P<pattern>.*)"'
)
def step_impl(context, ifc_class, property_path, pattern):
    import re

    pset_name, property_name = property_path.split(".")
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        prop = IfcStore.file.get_property(element, pset_name, property_name)
        if not prop:
            assert False
        # For now, we only check single values
        if prop.is_a("IfcPropertySingleValue"):
            if not (prop.NominalValue and re.search(pattern, prop.NominalValue.wrappedValue)):
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
    assert_elements(
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

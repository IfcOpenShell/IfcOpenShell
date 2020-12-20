from behave import step

from utils import IfcFile


@step("all {ifc_class} elements have an {aproperty} property in the {pset} pset")
def step_impl(context, ifc_class, aproperty, pset):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}
    from ifcopenshell.util.element import get_psets

    elements = IfcFile.get().by_type(ifc_class)
    elemcount = len(elements)
    for elem in elements:
        psets = get_psets(elem)
        if not (pset in psets and aproperty in psets[pset]):
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
        context.falseprops[elem.id()] = str(psets)

    falsecount = len(context.falseelems)
    if elemcount == 0:
        assert False, (
            "There are no {} elements in the IFC file."
            .format(ifc_class)
        )
    if falsecount == elemcount:
        assert False, (
            "All {} {} elements are missing "
            "the property {} in the pset {}."
            .format(elemcount, ifc_class, aproperty, pset)
        )
    if falsecount > 0:
        assert False, (
            "The following {} of {} {} elements are missing  "
            "the property {} in the pset {}: {}"
            .format(
                falsecount,
                elemcount,
                ifc_class,
                aproperty,
                pset,
                context.falseelems
            )
        )

    if len(context.falseelems) > 0:
        assert False, (
            "Some elemets missing the pset or property:\n{}"
            .format(context.falseguids)
        )


# ------------------------------------------------------------------------
# STEPS with Regular Expression Matcher ("re")
# ------------------------------------------------------------------------
use_step_matcher("re")


@step("all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property")
def step_impl(context, ifc_class, property_path):
    pset_name, property_name = property_path.split(".")
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        if not IfcFile.get_property(element, pset_name, property_name):
            assert False


@step(
    'all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property value matching the pattern "(?P<pattern>.*)"'
)
def step_impl(context, ifc_class, property_path, pattern):
    import re

    pset_name, property_name = property_path.split(".")
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        prop = IfcFile.get_property(element, pset_name, property_name)
        if not prop:
            assert False
        # For now, we only check single values
        if prop.is_a("IfcPropertySingleValue"):
            if not (prop.NominalValue and re.search(pattern, prop.NominalValue.wrappedValue)):
                assert False


# ------------------------------------------------------------------------
# STEPS with Parse Matcher ("parse")
# ------------------------------------------------------------------------
use_step_matcher("parse")


@step("all {ifc_class} elements have a {qto_name}.{quantity_name} quantity")
def step_impl(context, ifc_class, qto_name, quantity_name):
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        is_successful = False
        if not element.IsDefinedBy:
            assert False
        for relationship in element.IsDefinedBy:
            if relationship.RelatingPropertyDefinition.Name == qto_name:
                for quantity in relationship.RelatingPropertyDefinition.Quantities:
                    if quantity.Name == quantity_name:
                        is_successful = True
        if not is_successful:
            assert False


@step('the project has a {attribute_name} attribute with a value of "{attribute_value}"')
def step_impl(context, attribute_name, attribute_value):
    project = IfcFile.get().by_type("IfcProject")[0]
    assert getattr(project, attribute_name) == attribute_value


@step("all buildings have an address")
def step_impl(context):
    for building in IfcFile.get().by_type("IfcBuilding"):
        if not building.BuildingAddress:
            assert False, f'The building "{building.Name}" has no address.'

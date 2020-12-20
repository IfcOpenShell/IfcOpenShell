from behave import step

from attributes_eleclasses_methods import all_element_attribs_have_a_value
from attributes_eleclasses_methods import no_element_class
from utils import IfcFile
from utils import switch_locale


@step("there are no {ifc_class} elements because {reason}")
def step_impl(context, ifc_class, reason):
    switch_locale(context.localedir, "en")
    no_element_class(context, ifc_class, reason)


@step('all {ifc_class} elements have a name given')
def step_impl(context, ifc_class):

    context.falseelems = []
    context.falseguids = []

    elements = IfcFile.get().by_type(ifc_class)
    elemcount = len(elements)
    for elem in elements:
        # print(elem.Name)
        if not elem.Name:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
 
    falsecount = len(context.falseelems)
    if elemcount == 0:
        assert False, (
            "There are no {} elements in the IFC file."
            .format(ifc_class)
        )
    if falsecount == elemcount:
        assert False, (
            "The name of all {} {} elements is not set."
            .format(elemcount, ifc_class)
        )
    if falsecount > 0:
        assert False, (
            "The name of {} out of {} {} elements is not set."
            .format(falsecount, elemcount, ifc_class, context.falseelems)
        )


@step('all {ifc_class} elements have a description given')
def step_impl(context, ifc_class):

    context.falseelems = []
    context.falseguids = []

    elements = IfcFile.get().by_type(ifc_class)
    elemcount = len(elements)
    for elem in elements:
        # print(elem.Description)
        if not elem.Description:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
 
    falsecount = len(context.falseelems)
    if elemcount == 0:
        assert False, (
            "There are no {} elements in the IFC file."
            .format(ifc_class)
        )
    if falsecount == elemcount:
        assert False, (
            "The description of all {} {} elements is not set."
            .format(elemcount, ifc_class)
        )
    if falsecount > 0:
        assert False, (
            "The description of {} out of {} {} elements is not set."
            .format(falsecount, elemcount, ifc_class, context.falseelems)
        )


@step('all {ifc_class} elements class attributes have a value')
def step_impl(context, ifc_class):
    switch_locale(context.localedir, "en")
    all_element_attribs_have_a_value(context, ifc_class)



@step('all {ifc_class} elements have a name matching the pattern "{pattern}"')
def step_impl(context, ifc_class, pattern):
    import re

    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        if not re.search(pattern, element.Name):
            assert False


@step('there is an {ifc_class} element with a {attribute_name} attribute with a value of "{attribute_value}"')
def step_impl(context, ifc_class, attribute_name, attribute_value):
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        if hasattr(element, attribute_name) and getattr(element, attribute_name) == attribute_value:
            return
    assert False


# ------------------------------------------------------------------------
# STEPS with Regular Expression Matcher ("re")
# ------------------------------------------------------------------------
use_step_matcher("re")


@step("all (?P<ifc_class>.*) elements have an? (?P<attribute>.*) attribute")
def step_impl(context, ifc_class, attribute):
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        if not getattr(element, attribute):
            assert False


@step('all (?P<ifc_class>.*) elements have an? (?P<attribute>.*) matching the pattern "(?P<pattern>.*)"')
def step_impl(context, ifc_class, attribute, pattern):
    import re

    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        value = getattr(element, attribute)
        print(f'Checking value "{value}" for {element}')
        assert re.search(pattern, value)


@step('all (?P<ifc_class>.*) elements have an? (?P<attributes>.*) taken from the list in "(?P<list_file>.*)"')
def step_impl(context, ifc_class, attributes, list_file):
    import csv

    values = []
    with open(list_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            values.append(row)
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        attribute_values = []
        for attribute in attributes.split(","):
            if not hasattr(element, attribute):
                assert False, f"Failed at element {element.GlobalId}"
            attribute_values.append(getattr(element, attribute))
        if attribute_values not in values:
            assert False, f"Failed at element {element.GlobalId}"

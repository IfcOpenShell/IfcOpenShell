from behave import step

import attributes_eleclasses_methods as aem
from utils import assert_elements
from utils import IfcFile


@step("There are no {ifc_class} elements")
def step_impl(context, ifc_class):
    aem.no_eleclass(context, ifc_class)


@step("There are no {ifc_class} elements because {reason}")
def step_impl(context, ifc_class, reason):
    aem.no_eleclass(context, ifc_class)


@step("All {ifc_class} elements class attributes have a value")
def step_impl(context, ifc_class):
    aem.eleclass_have_class_attributes_with_a_value(context, ifc_class)


@step("All {ifc_class} elements have a name given")
def step_impl(context, ifc_class):
    aem.eleclass_has_name_with_a_value(context, ifc_class)


@step("All {ifc_class} elements have a description given")
def step_impl(context, ifc_class):
    aem.eleclass_has_description_with_a_value(context, ifc_class)


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

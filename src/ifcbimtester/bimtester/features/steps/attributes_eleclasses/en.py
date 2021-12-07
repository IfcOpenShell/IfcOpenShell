import ifcopenshell.util.element as eleutils

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('There are exclusively "{ifc_classes}" elements only')
def step_impl(context, ifc_classes):
    only_eleclasses(
        context,
        ifc_classes
    )


@step('There are no "{ifc_class}" elements')
def step_impl(context, ifc_class):
    no_eleclass(
        context,
        ifc_class
    )


@step('There are no "{ifc_class}" elements because "{reason}"')
def step_impl(context, ifc_class, reason):
    no_eleclass(
        context,
        ifc_class
    )


@step('All "{ifc_class}" elements class attributes have a value')
def step_impl(context, ifc_class):
    eleclass_have_class_attributes_with_a_value(
        context,
        ifc_class
    )


@step('All "{ifc_class}" elements have a name given')
def step_impl(context, ifc_class):
    eleclass_has_name_with_a_value(
        context,
        ifc_class
    )


@step('All "{ifc_class}" elements have a description given')
def step_impl(context, ifc_class):
    eleclass_has_description_with_a_value(
        context,
        ifc_class
    )


@step('All "{ifc_class}" elements have a name matching the pattern "{pattern}"')
def step_impl(context, ifc_class, pattern):
    import re

    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        if not re.search(pattern, element.Name):
            assert False


@step('There is an "{ifc_class}" element with a "{attribute_name}" attribute with a value of "{attribute_value}"')
def step_impl(context, ifc_class, attribute_name, attribute_value):
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        if hasattr(element, attribute_name) and getattr(element, attribute_name) == attribute_value:
            return
    assert False


# ************************************************************************************************
# helper
def only_eleclasses(
    context, ifc_classes
):

    context.falseelems = []
    context.falseguids = []

    # get the list of ifc_classes
    target_ifc_classes = ifc_classes.replace(" ","").split(",")
    # ToDo test if they exist in ifc standard, should be possible with ifcos

    all_elements = IfcStore.file.by_type("IfcBuildingElement")
    context.elemcount = len(all_elements)

    false_elements = []
    for elem in all_elements:
        if elem.is_a() not in target_ifc_classes:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
    context.falsecount = len(context.falseelems)

    # use ifc_classes in method parameter but ifc_class in string parameter
    # be careful somehow the opposite of most other tests is tested
    util.assert_elements(
        ifc_classes,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} elements in the file are not {ifc_class} elements."),
        message_some_falseelems=_("{falsecount} of {elemcount} false_elements are not {ifc_class} elements: {falseelems}"),
    )


def no_eleclass(
    context, ifc_class
):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    context.elemcount = len(IfcStore.file.by_type("IfcBuildingElement"))
    for elem in elements:
        context.falseelems.append(str(elem))
        context.falseguids.append(elem.GlobalId)
    context.falsecount = len(context.falseelems)

    # be careful somehow the opposite of most other tests is tested
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} elements in the file are {ifc_class} elements."),
        message_some_falseelems=_("{falsecount} of {elemcount} false_elements are {ifc_class} elements: {falseelems}"),
    )


def eleclass_have_class_attributes_with_a_value(
    context, ifc_class
):

    from ifcopenshell.ifcopenshell_wrapper import schema_by_name
    # schema = schema_by_name("IFC2X3")
    schema = schema_by_name(IfcStore.file.schema)
    class_attributes = []
    for cl_attrib in schema.declaration_by_name(ifc_class).all_attributes():
        class_attributes.append(cl_attrib.name())
    # print(class_attributes)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcStore.file.by_type(ifc_class)
    failed_attribs = []
    for elem in elements:
        elem_failed = False
        for cl_attrib in class_attributes:
            attrib_value = getattr(elem, cl_attrib)
            if not attrib_value:
                elem_failed = True
                failed_attribs.append(cl_attrib)
                # print(attrib_value)
        if elem_failed is True:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = failed_attribs

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("For all {elemcount} {ifc_class} elements at least one of these class attributes {parameter} has no value."),
        message_some_falseelems=_("For the following {falsecount} out of {elemcount} {ifc_class} elements at least one of these class attributes {parameter} has no value: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=failed_attribs
    )


def eleclass_has_name_with_a_value(context, ifc_class):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        # print(elem.Name)
        if not elem.Name:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
 
    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The name of all {elemcount} elements is not set."),
        message_some_falseelems=_("The name of {falsecount} out of {elemcount} {ifc_class} elements is not set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_has_description_with_a_value(
    context, ifc_class
):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        # print(elem.Description)
        if not elem.Description:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
 
    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The description of all {elemcount} elements is not set."),
        message_some_falseelems=_("The description of {falsecount} out of {elemcount} {ifc_class} elements is not set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )



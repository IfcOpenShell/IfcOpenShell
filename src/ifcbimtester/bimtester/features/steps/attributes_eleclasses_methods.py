import gettext  # noqa

from utils import assert_elements
from utils import IfcFile


def no_eleclass(
    context, ifc_class
):

    context.falseelems = []
    context.falseguids = []

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        context.falseelems.append(str(elem))
        context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)

    if context.elemcount == 0 and context.falsecount == 0:
        return  # Test OK, thus we can not use the assert_elements method
    elif context.falsecount == context.elemcount:
        assert False, (
            _("All {elemcount} elements in the file are {ifc_class}.")
            .format(
                elemcount=context.elemcount,
                ifc_class=ifc_class
            )
        )
    elif context.falsecount > 0 and fcontext.alsecount < context.elemcount:
        assert False, (
            _("{falsecount} of {elemcount} element are {ifc_class} elements: {falseelems}")
            .format(
                falsecount=context.falsecount,
                elemcount=context.elemcount,
                ifc_class=ifc_class,
                falseelems=context.falseelems,
            )
        )
    else:
        assert False, _("Error in falsecount, something went wrong.")


def eleclass_have_class_attributes_with_a_value(
    context, ifc_class
):

    from ifcopenshell.ifcopenshell_wrapper import schema_by_name
    # schema = schema_by_name("IFC2X3")
    schema = schema_by_name(IfcFile.get().schema)
    class_attributes = []
    for cl_attrib in schema.declaration_by_name(ifc_class).all_attributes():
        class_attributes.append(cl_attrib.name())
    # print(class_attributes)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        failed_attribs = []
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
    assert_elements(
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

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        # print(elem.Name)
        if not elem.Name:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
 
    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The name of all {elemcount} {elemcount} elements is not set."),
        message_some_falseelems=_("The name of {falsecount} out of {elemcount} {ifc_class} elements is not set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_has_description_with_a_value(
    context, ifc_class
):

    context.falseelems = []
    context.falseguids = []

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        # print(elem.Description)
        if not elem.Description:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
 
    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The description of all {elemcount} {elemcount} elements is not set."),
        message_some_falseelems=_("The description of {falsecount} out of {elemcount} {ifc_class} elements is not set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )

import gettext  # noqa
from utils import assert_elements
from utils import IfcFile


def no_element_class_ele(context, ifc_class, reason):

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

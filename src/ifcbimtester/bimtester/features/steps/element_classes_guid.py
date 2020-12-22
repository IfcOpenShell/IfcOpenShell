from behave import step

from utils import assert_attribute
from utils import assert_type
from utils import IfcFile


@step("The element {guid} is an {ifc_class} only")
def step_impl(context, guid, ifc_class):
    element = IfcFile.by_guid(guid)
    assert_type(element, ifc_class, is_exact=True)


@step("The element {guid} is an {ifc_class}")
def step_impl(context, guid, ifc_class):
    element = IfcFile.by_guid(guid)
    assert_type(element, ifc_class)


@step("The element {guid} is further defined as a {predefined_type}")
def step_impl(context, guid, predefined_type):
    element = IfcFile.by_guid(guid)
    if (
        hasattr(element, "PredefinedType")
        and element.PredefinedType == "USERDEFINED"
        and hasattr(element, "ObjectType")
    ):
        assert_attribute(element, "ObjectType", predefined_type)
    elif hasattr(element, "PredefinedType"):
        assert_attribute(element, "PredefinedType", predefined_type)
    else:
        assert False, "The element {} does not have a PredefinedType or ObjectType attribute".format(element)


@step("The element {guid} should not exist because {reason}")
def step_impl(context, guid, reason):
    try:
        element = IfcFile.get().by_id(guid)
    except:
        return
    assert False, "This element {} should be reevaluated.".format(element)

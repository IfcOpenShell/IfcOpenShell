import ifcopenshell
from behave import given, when, then, step

@given('the IFC file "{file}"')
def step_impl(context, file):
    context.file = ifcopenshell.open(file)

@then('the element {id} is an {ifc_class}')
def step_impl(context, id, ifc_class):
    assert context.file.by_id(id).is_a(ifc_class)

@then('the element {id} should not exist because {reason}')
def step_impl(context, id, reason):
    assert not context.file.by_id(id)

import ifcopenshell
from behave import given, when, then, step

class IfcFile(object):
    file = None

    @classmethod
    def load(cls, path=None):
        cls.file = ifcopenshell.open(path)

    @classmethod
    def get(cls):
        return cls.file

@given('the IFC file "{file}"')
def step_impl(context, file):
    IfcFile.load(file)

@given('the IFC file "{file}" exists')
def step_impl(context, file):
    assert True

@given('that an IFC file is loaded')
def step_impl(context):
    assert IfcFile.get()

@then('the file should be an {schema} file')
def step_impl(context, schema):
    assert IfcFile.get().schema == schema

@then('the element {id} is an {ifc_class}')
def step_impl(context, id, ifc_class):
    assert IfcFile.get().by_id(id).is_a(ifc_class)

@then('the element {id} should not exist because {reason}')
def step_impl(context, id, reason):
    assert not IfcFile.get().by_id(id)

@then('the file is exempt from auditing because {reason}')
def step_impl(context, id, reason):
    assert True

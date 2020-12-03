from behave import step

from utils import IfcFile


@step('The IFC file "{file}" must be provided')
def step_impl(context, file):
    try:
        IfcFile.load(file)
    except:
        assert False, f"The file {file} could not be loaded"


@step("IFC data must use the {schema} schema")
def step_impl(context, schema):
    assert IfcFile.get().schema == schema, "We expected a schema of {} but instead got {}".format(
        schema, IfcFile.get().schema
    )


@step('The IFC file "{file}" is exempt from being provided')
def step_impl(context, file):
    pass


@step("No further requirements are specified because {reason}")
def step_impl(context, reason):
    pass

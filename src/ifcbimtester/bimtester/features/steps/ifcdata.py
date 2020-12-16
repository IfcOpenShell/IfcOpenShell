from behave import step

from utils import assert_schema
from utils import IfcFile


@step('The IFC file "{file}" must be provided')
def step_impl(context, file):
    try:
        IfcFile.load(file)
    except:
        assert False, f"The file {file} could not be loaded"


@step("IFC data must use the {schema} schema")
def step_impl(context, schema):
    context.schema = IfcFile.get().schema
    assert_schema(schema, context.schema)
    

@step('The IFC file "{file}" is exempt from being provided')
def step_impl(context, file):
    pass


@step("No further requirements are specified because {reason}")
def step_impl(context, reason):
    pass


@step("The IFC file must be exported by application full name {fullname}")
def step_impl(context, fullname):

    real_fullname = IfcFile.get().by_type("IfcApplication")[0].ApplicationFullName
    assert  real_fullname == fullname , (
        "The IFC file was not exported by application full name {} "
        "instead it was exported by application full name {}"
        .format(fullname, real_fullname)
    )


@step("The IFC file must be exported by application identifier {identifier}")
def step_impl(context, identifier):

    real_identifier = IfcFile.get().by_type("IfcApplication")[0].ApplicationIdentifier
    assert  real_identifier == identifier , (
        "The IFC file was not exported by application identifier {} "
        "instead it was exported by identifier {}"
        .format(identifier, real_identifier)
    )


@step("The IFC file must be exported by the application version {version}")
def step_impl(context, version):

    real_version = IfcFile.get().by_type("IfcApplication")[0].Version
    assert  real_version == version , (
        "The IFC file was not exported by application version {} "
        "instead it was exported by version {}"
        .format(version, real_version)
    )


@step("IFC data header must have a file description of {header_file_description} such as the new Allplan IFC exporter creates it")
def step_impl(context, header_file_description):
    
    is_header_file_description = IfcFile.get().wrapped_data.header.file_description.description
    assert  str(is_header_file_description) == header_file_description , (
        "The file was not exported by the new ifc exporter in Allplan. File description header: {}"
        .format(is_header_file_description)
    )

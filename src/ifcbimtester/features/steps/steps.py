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


@then('all {ifc_class} elements have a name matching the pattern "{pattern}"')
def step_impl(context, ifc_class, pattern):
    import re
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        if not re.search(pattern, element.Name):
            assert False
    assert True


@then('all {ifc_class} elements have an {representation_class} representation')
def step_impl(context, ifc_class, representation_class):
    def is_item_a_representation(item, representation):
        if '/' in representation:
            for cls in representation.split('/'):
                if item.is_a(cls):
                    return True
        elif item.is_a(representation):
            return True

    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        if not element.Representation:
            continue
        has_representation = False
        for representation in element.Representation.Representations:
            for item in representation.Items:
                if item.is_a('IfcMappedItem'):
                    # We only check one more level deep.
                    for item2 in item.MappingSource.MappedRepresentation.Items:
                        if is_item_a_representation(item2, representation_class):
                            has_representation = True
                else:
                    if is_item_a_representation(item, representation_class):
                        has_representation = True
        if not has_representation:
            assert False
    assert True

use_step_matcher('re')
@then('all (?P<ifc_class>.*) elements have an? (?P<attribute>.*) attribute')
def step_impl(context, ifc_class, attribute):
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        if not getattr(element, attribute):
            assert False
    assert True


@then('all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property')
def step_impl(context, ifc_class, property_path):
    pset_name, property_name = property_path.split('.')
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        is_successful = False
        if not element.IsDefinedBy:
            assert False
        for relationship in element.IsDefinedBy:
            if relationship.RelatingPropertyDefinition.Name == pset_name:
                for prop in relationship.RelatingPropertyDefinition.HasProperties:
                    if prop.Name == property_name:
                        is_successful = True
        if not is_successful:
            assert False
    assert True


@then('all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property value matching pattern "(?P<pattern>.*)"')
def step_impl(context, ifc_class, property_path, pattern):
    import re
    pset_name, property_name = property_path.split('.')
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        is_successful = False
        if not element.IsDefinedBy:
            assert False
        for relationship in element.IsDefinedBy:
            if relationship.RelatingPropertyDefinition.Name == pset_name:
                for prop in relationship.RelatingPropertyDefinition.HasProperties:
                    if prop.Name == property_name:
                        # For now, we only check single values
                        if prop.is_a('IfcPropertySingleValue'):
                            if prop.NominalValue \
                                    and re.search(pattern, prop.NominalValue):
                                is_successful = True
        if not is_successful:
            assert False
    assert True


use_step_matcher('parse')
@then('all {ifc_class} elements have a {qto_name}.{quantity_name} quantity')
def step_impl(context, ifc_class, qto_name, quantity_name):
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        is_successful = False
        if not element.IsDefinedBy:
            assert False
        for relationship in element.IsDefinedBy:
            if relationship.RelatingPropertyDefinition.Name == qto_name:
                for quantity in relationship.RelatingPropertyDefinition.Quantities:
                    if quantity.Name == quantity_name:
                        is_successful = True
        if not is_successful:
            assert False
    assert True

from behave import step, given, when, then, use_step_matcher

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.table import TableModel

use_step_matcher("parse")


@step('There must be exactly {number} "{ifc_class}" element')
@step('There must be exactly {number} "{ifc_class}" elements')
def step_impl(context, number, ifc_class):
    num = len(IfcStore.file.by_type(ifc_class))
    assert num == int(
        number
    ), "Could not find {} elements of {}. \
        Found {} element(s).".format(
        number, ifc_class, num
    )


@given('a set of (key,value) called ("{key_name}","{value_name}")')
def step_impl(context, key_name, value_name):
    model = getattr(context, "model", None)
    if not model:
        context.model = TableModel(key_name, value_name)
    for row in context.table:
        context.model.add_row(row[key_name], row[value_name])


@given('a set of (key,value) called ("{key_name}","{value_name}") taken from the file "{path_file}"')
def step_impl(context, key_name, value_name, path_file):
    import csv
    import os

    model = getattr(context, "model", None)
    if not model:
        context.model = TableModel(key_name, value_name)
    if context.config.userdata.get("path"):
        path_file = os.path.join(context.config.userdata.get("path"), path_file)
    if not os.path.exists(path_file):
        assert False, "File {} not found".format(path_file)
    with open(path_file, "r", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            context.model.add_row(row[key_name], row[value_name])


@then('there is an element of type key with an attribute "{attribute_name}" equals to value')
def step_impl(context, attribute_name):
    if not context.model.key_name and not context.model.value_name:
        assert False, "Missing (key,value)"
    errors = []
    rows = context.model.rows
    for key, values in rows.items():
        for value in values:
            found = check_equals(attribute_name, value, IfcStore.file.by_type(key))
            if not found:
                errors.append(f"The row ({key}, {value}) was not found.")
    assert not errors, "Errors occured:\n{}".format("\n".join(errors))


@then('there is an element of type key with an attribute "{attribute_name}" starting with value')
def step_impl(context, attribute_name):
    # import re
    if not context.model.key_name and not context.model.value_name:
        assert False, "Missing (key,value)"
    errors = []
    rows = context.model.rows
    for key, values in rows.items():
        for value in values:
            found = check_starts_with(attribute_name, value, IfcStore.file.by_type(key))
            if not found:
                errors.append(f"The row ({key}, {value}) was not found.")
    assert not errors, "Errors occured:\n{}".format("\n".join(errors))


@then('there must be exactly a number of "{ifc_class}" equals to the number of distinct value')
def step_impl(context, ifc_class):
    try:
        context.execute_steps(
            """
            then There must be exactly {number} "{ifc_class}" elements
            """.format(
                ifc_class=ifc_class, number=context.model.get_count_distinct_values()
            )
        )
    except AssertionError as error:
        str_error = str(error)
        assert False, str_error[: str_error.find("Traceback")]
    assert True


@then('there is a relationship "{ifc_class}" between the two elements of each row')
def step_impl(context, ifc_class):
    if not context.model.key_name and not context.model.value_name:
        assert False, "Missing (key,value)"
    errors = []
    elements = IfcStore.file.by_type(ifc_class)

    # first, loop on the dataset to check if there are all in the relationships
    rows = context.model.rows
    for key, values in rows.items():
        found = False
        # value is actually a list of values
        for value in values:
            for element in elements:
                if (
                    any(x.Name == key for x in getattr(element, context.model.key_name))
                    and getattr(element, context.model.value_name).Name == value
                ):
                    found = True
            if not found:
                errors.append(f"The row ({key}, {value}) does not have the relationship.")

    # second, loop on the elements to check if there are not too many relationships
    for element in elements:
        if hasattr(element, context.model.key_name) and hasattr(element, context.model.value_name):
            # list here
            keys = getattr(element, context.model.key_name)
            value = getattr(element, context.model.value_name).Name
            for key in keys:
                if not key.Name in rows or not value in rows[key.Name]:
                    errors.append(f"The element ({element}) has a relation that cannot be found in the dataset: {key}")
    assert not errors, "Errors occured:\n{}".format("\n".join(errors))


use_step_matcher("re")


@step('all IfcGroup must be linked to a type "(?P<linked_ifc_classes>.*)"')
def step_impl(context, linked_ifc_classes):
    groups = IfcStore.file.by_type("IfcGroup")
    errors = []
    for group in groups:
        if not hasattr(group, "IsGroupedBy"):
            errors.append(f'The element "{group.Name}" has no "IsGroupedBy" attribute.')
        else:
            for grouped_by in getattr(group, "IsGroupedBy"):
                if not hasattr(grouped_by, "RelatedObjects"):
                    errors.append(f'The element "{grouped_by.Name}" has no "RelatedObjects" attribute.')
                else:
                    for related_object in getattr(grouped_by, "RelatedObjects"):
                        found = False
                        for linked_ifc_class in linked_ifc_classes.split(","):
                            if related_object.is_a(linked_ifc_class):
                                found = True
                        if not found:
                            errors.append(
                                f'The element "{related_object.Name}" does not have the right associated type.'
                            )
    assert not errors, "Errors occured:\n{}".format("\n".join(errors))


@then('there is an element of type "(?P<ifc_types>.*)" with an attribute "(?P<attribute_name>.*)" for each key')
def step_impl(context, ifc_types, attribute_name):
    check_if_element_exists_by_types_with_attribute_name(ifc_types, attribute_name, context.model.rows.keys())


@then('there is an element of type "(?P<ifc_types>.*)" with an attribute "(?P<attribute_name>.*)" for each value')
def step_impl(context, ifc_types, attribute_name):
    values = set(item for sublist in context.model.rows.values() for item in sublist)
    check_if_element_exists_by_types_with_attribute_name(ifc_types, attribute_name, values)


def check_if_element_exists_by_types_with_attribute_name(ifc_types, attribute_name, attribute_values):
    errors = []
    # retrieve all elements of that type
    elements = util.by_types(IfcStore.file, ifc_types)
    # loop
    for attribute_value in attribute_values:
        found = False
        for element in elements:
            if hasattr(element, attribute_name) and getattr(element, attribute_name) == attribute_value:
                found = True
        if not found:
            errors.append(f'An element with attribute "{attribute_name}" equals to "{attribute_value}" was not found.')
    assert not errors, "Errors occured:\n{}".format("\n".join(errors))


def check_starts_with(attribute_name, value, elements):
    """Make sure at least an element of the list has a attribute starting with the value"""
    if any(hasattr(x, attribute_name) and getattr(x, attribute_name).startswith(value) for x in elements):
        return True
    return False


def check_equals(attribute_name, value, elements):
    """Make sure at least an element of the list has a attribute equals to the value"""
    if any(hasattr(x, attribute_name) and getattr(x, attribute_name) == value for x in elements):
        return True
    return False

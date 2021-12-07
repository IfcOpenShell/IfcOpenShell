from behave import step, given, when, then, use_step_matcher

use_step_matcher("parse")


@given("a set of specific related elements")
def step_impl(context):
    model = getattr(context, "model", None)
    if not model:
        context.model = TableModel()
    for row in context.table:
        context.model.add_row(row["RelatedObjects"], row["RelatingGroup"])


@given('a set of specific related elements taken from the file "{path_file}"')
def step_impl(context, path_file):
    import csv
    import os

    model = getattr(context, "model", None)
    if not model:
        context.model = TableModel()
    if context.config.userdata.get("path"):
        path_file = os.path.join(context.config.userdata.get("path"), path_file)
    if not os.path.exists(path_file):
        assert False, "File {} not found".format(path_file)
    with open(path_file, "r", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            context.model.add_row(row["RelatedObjects"], row["RelatingGroup"])


@then("there must be exactly a number of {ifc_class} equals to the number of distinct row value")
def step_impl(context, ifc_class):
    try:
        context.execute_steps(
            """
            then There must be exactly {number} {ifc_class} elements
            """.format(
                ifc_class=ifc_class, number=context.model.get_count_distinct_values()
            )
        )
    except AssertionError as error:
        str_error = str(error)
        assert False, str_error[: str_error.find("Traceback")]
    assert True


@then(
    "there is a relationship {ifc_class} with {left_attribute} and {right_attribute} between the two elements of each row"
)
def step_impl(context, ifc_class, left_attribute, right_attribute):
    rows = context.model.rows
    elements = IfcStore.file.by_type(ifc_class)
    errors = []
    for key, value in rows.items():
        found = False
        for element in elements:
            if (
                any(x.Name == key for x in getattr(element, left_attribute))
                and getattr(element, right_attribute).Name == value
            ):
                found = True
        if not found:
            errors.append(f"The row ({key}, {value}) does not have the relationship.")
    assert not errors, "Errors occured:\n{}".format("\n".join(errors))


use_step_matcher("re")


@step("all IfcGroup must be linked to a type in the list (?P<linked_ifc_classes>.*)")
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


@then("there is an element of type (?P<ifc_types>.*) with a (?P<attribute_name>.*) attribute for each row key")
def step_impl(context, ifc_types, attribute_name):
    check_if_element_exists_by_types_with_attribute_name(ifc_types, attribute_name, context.model.rows.keys())


@then("there is an element of type (?P<ifc_types>.*) with a (?P<attribute_name>.*) attribute for each row value")
def step_impl(context, ifc_types, attribute_name):
    values = set(context.model.rows.values())
    check_if_element_exists_by_types_with_attribute_name(ifc_types, attribute_name, values)


def check_if_element_exists_by_types_with_attribute_name(ifc_types, attribute_name, attribute_values):
    errors = []

    elements = []
    for ifc_type in ifc_types.split(","):
        elements += ifc.by_type(ifc_type.strip())

    for attribute_value in attribute_values:
        found = False
        for element in elements:
            if hasattr(element, attribute_name) and getattr(element, attribute_name) == attribute_value:
                found = True
        if not found:
            errors.append(f'An element with {attribute_name} attribute "{attribute_value}" was not found.')
    assert not errors, "Errors occured:\n{}".format("\n".join(errors))


class TableModel(object):
    """This class represents a table of data."""

    def __init__(self):
        self.rows = dict()

    def add_row(self, related, relating):
        self.rows[related] = relating

    def get_count(self):
        return len(self.rows)

    def get_count_distinct_values(self):
        return len(set(self.rows.values()))

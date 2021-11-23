import json
from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


def get_classification(name):
    classifications = [c for c in IfcStore.file.by_type("IfcClassification") if c.Name == name]
    if len(classifications) != 1:
        assert False, f'The classification "{name}" was not found'
    return classifications[0]


@step('The classification "{name}" must be used')
def step_impl(context, name):
    get_classification(name)


@step('The classification "{name}" is published by "{source}"')
def step_impl(context, name, source):
    util.assert_attribute(get_classification(name), "Source", source)


@step('The classification "{name}" is the edition "{edition}" on "{edition_date}"')
def step_impl(context, name, edition, edition_date):
    element = get_classification(name)
    util.assert_attribute(element, "Edition", edition)
    util.assert_attribute(element, "EditionDate", edition_date)


@step('The classification "{name}" has the description "{description}"')
def step_impl(context, name, description):
    util.assert_attribute(get_classification(name), "Description", description)


@step('The classification "{name}" is referenced by the website "{location}"')
def step_impl(context, name, location):
    util.assert_attribute(get_classification(name), "Location", location)


@step('The classification "{name}" has a hierarchy denoted by the tokens "{tokens}"')
def step_impl(context, name, tokens):
    try:
        tokens = json.loads(tokens)
    except:
        assert False, _("Tokens {} are not specified as a JSON list").format(tokens)
    util.assert_attribute(get_classification(name), "ReferenceTokens", tokens)


@step('The element "{guid}" is classified as a "{identification}" with name "{reference_name}"')
def step_impl(context, guid, identification, reference_name):
    element = util.assert_guid(IfcStore.file, guid)
    if not hasattr(element, "HasAssociations") or not element.HasAssociations:
        assert False, _("The element {} has no associations.").format(element)
    references = [a.RelatingClassification for a in element.HasAssociations if a.is_a("IfcRelAssociatesClassification")]
    if not references:
        assert False, _("The element {element} has no associated classification references.").format(element)
    is_success = False
    for reference in references:
        try:
            util.assert_attribute(reference, "Identification", identification)
            util.assert_attribute(reference, "Name", reference_name)
            is_success = True
        except:
            pass
    if not is_success:
        assert False, _(
            "No classification references met the requirement for an identification {} and name {} for the element {}.  The references we found were: {}"
        ).format(identification, reference_name, element, references)

from behave import step
from utils import IfcFile, assert_attribute, assert_type

def check_geocode_attribute(guid, ifc_class, name, value):
    element = IfcFile.by_guid(guid)
    assert_type(element, ifc_class)
    assert_attribute(element, name, value)


def check_geocode_address(guid, ifc_class, name, value):
    element = IfcFile.by_guid(guid)
    assert_type(element, ifc_class)
    if ifc_class == 'IfcSite':
        address_name = 'SiteAddress'
    elif ifc_class == 'IfcBuilding':
        address_name = 'BuildingAddress'
    assert_attribute(element, address_name)
    assert_attribute(getattr(element, address_name), name, value)


use_step_matcher('re')
@step('The (site|building|facility) (?P<guid>.*) has a name of (?P<name>.*)')
def step_impl(context, _unused, guid, name):
    check_geocode_attribute(guid, 'IfcSite', 'Name', name)


@step('The (site|building|facility) (?P<guid>.*) has a description of (?P<description>.*)')
def step_impl(context, _unused, guid, description):
    check_geocode_attribute(guid, 'IfcSite', 'Description', description)


@step('The (site|building) (?P<guid>.*) has a land title number of (?P<land_title_number>.*)')
def step_impl(context, _unused, guid, land_title_number):
    check_geocode_attribute(guid, 'IfcSite', 'LandTitleNumber', land_title_number)


@step('The (site|building) (?P<guid>.*) has the address "(?P<address_lines>.*)"')
def step_impl(context, _unused, guid, address_lines):
    check_geocode_address(guid, 'IfcSite', 'AddressLines', address_lines.split('\\n'))


@step('The (site|building) (?P<guid>.*) has a postal box of (?P<postal_box>.*)')
def step_impl(context, _unused, guid, postal_box):
    check_geocode_address(guid, 'IfcSite', 'PostalBox', postal_box)


@step('The (site|building) (?P<guid>.*) is in the town (?P<town>.*)')
def step_impl(context, _unused, guid, town):
    check_geocode_address(guid, 'IfcSite', 'Town', town)


@step('The (site|building) (?P<guid>.*) is in the region (?P<region>.*)')
def step_impl(context, _unused, guid, region):
    check_geocode_address(guid, 'IfcSite', 'Region', region)


@step('The (site|building) (?P<guid>.*) has a post code of (?P<post_code>.*)')
def step_impl(context, _unused, guid, post_code):
    check_geocode_address(guid, 'IfcSite', 'PostalCode', post_code)


@step('The (site|building) (?P<guid>.*) is in the country (?P<country>.*)')
def step_impl(context, _unused, guid, country):
    check_geocode_address(guid, 'IfcSite', 'Country', country)


@step('The (site|building) (?P<guid>.*) has an address description of (?P<description>.*)')
def step_impl(context, _unused, guid, description):
    check_geocode_address(guid, 'IfcSite', 'Description', description)

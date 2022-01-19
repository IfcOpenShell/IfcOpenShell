# BIMTester - OpenBIM Auditing Tool
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BIMTester.
#
# BIMTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BIMTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BIMTester.  If not, see <http://www.gnu.org/licenses/>.

from behave import step, use_step_matcher

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


def get_ifc_class_from_spatial_type(spatial_type):
    if spatial_type == "site":
        return "IfcSite"
    elif spatial_type == "building":
        return "IfcBuilding"
    return "IfcFacility"


def check_geocode_attribute(guid, spatial_type, name, value):
    element = util.assert_guid(IfcStore.file, guid)
    util.assert_type(element, get_ifc_class_from_spatial_type(spatial_type))
    util.assert_attribute(element, name, value)


def check_geocode_address(guid, spatial_type, name, value):
    element = util.assert_guid(IfcStore.file, guid)
    ifc_class = get_ifc_class_from_spatial_type(spatial_type)
    util.assert_type(element, ifc_class)
    if ifc_class == "IfcSite":
        address_name = "SiteAddress"
    elif ifc_class == "IfcBuilding":
        address_name = "BuildingAddress"
    util.assert_attribute(element, address_name)
    util.assert_attribute(getattr(element, address_name), name, value)


use_step_matcher("re")


@step('The (site|building|facility) "(?P<guid>.*)" has a name of "(?P<name>.*)"')
def step_impl(context, spatial_type, guid, name):
    check_geocode_attribute(guid, spatial_type, "Name", name)


@step('The (site|building|facility) "(?P<guid>.*)" has a description of "(?P<description>.*)"')
def step_impl(context, spatial_type, guid, description):
    check_geocode_attribute(guid, spatial_type, "Description", description)


@step('The site "(?P<guid>.*)" has a land title number of "(?P<land_title_number>.*)"')
def step_impl(context, guid, land_title_number):
    check_geocode_attribute(guid, "site", "LandTitleNumber", land_title_number)


@step('The (site|building) "(?P<guid>.*)" has the address "(?P<address_lines>.*)"')
def step_impl(context, spatial_type, guid, address_lines):
    check_geocode_address(guid, spatial_type, "AddressLines", address_lines.split("\\n"))


@step('The (site|building) "(?P<guid>.*)" has a postal box of "(?P<postal_box>.*)"')
def step_impl(context, spatial_type, guid, postal_box):
    check_geocode_address(guid, spatial_type, "PostalBox", postal_box)


@step('The (site|building) "(?P<guid>.*)" is in the town "(?P<town>.*)"')
def step_impl(context, spatial_type, guid, town):
    check_geocode_address(guid, spatial_type, "Town", town)


@step('The (site|building) "(?P<guid>.*)" is in the region "(?P<region>.*)"')
def step_impl(context, spatial_type, guid, region):
    check_geocode_address(guid, spatial_type, "Region", region)


@step('The (site|building) "(?P<guid>.*)" has a post code of "(?P<post_code>.*)"')
def step_impl(context, spatial_type, guid, post_code):
    check_geocode_address(guid, spatial_type, "PostalCode", post_code)


@step('The (site|building) "(?P<guid>.*)" is in the country "(?P<country>.*)"')
def step_impl(context, spatial_type, guid, country):
    check_geocode_address(guid, spatial_type, "Country", country)


@step('The (site|building) "(?P<guid>.*)" has an address description of "(?P<description>.*)"')
def step_impl(context, spatial_type, guid, description):
    check_geocode_address(guid, spatial_type, "Description", description)

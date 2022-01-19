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

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('The element "{guid}" is an "{ifc_class}" only')
def step_impl(context, guid, ifc_class):
    element = util.assert_guid(IfcStore.file, guid)
    util.assert_type(element, ifc_class, is_exact=True)


@step('The element "{guid}" is an "{ifc_class}"')
def step_impl(context, guid, ifc_class):
    element = util.assert_guid(IfcStore.file, guid)
    util.assert_type(element, ifc_class)


@step('The element "{guid}" is further defined as a "{predefined_type}"')
def step_impl(context, guid, predefined_type):
    element = util.assert_guid(IfcStore.file, guid)
    if (
        hasattr(element, "PredefinedType")
        and element.PredefinedType == "USERDEFINED"
        and hasattr(element, "ObjectType")
    ):
        util.assert_attribute(element, "ObjectType", predefined_type)
    elif hasattr(element, "PredefinedType"):
        util.assert_attribute(element, "PredefinedType", predefined_type)
    else:
        assert False, _("The element {} does not have a PredefinedType or ObjectType attribute").format(element)


@step('The element "{guid}" should not exist because "{reason}"')
def step_impl(context, guid, reason):
    try:
        element = IfcStore.file.by_id(guid)
    except:
        return
    assert False, _("This element {} should be reevaluated.").format(element)

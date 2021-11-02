# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import blenderbim.core.attribute as subject
from test.core.bootstrap import ifc


class TestCopyAttributeToSelection:
    def test_run(self, ifc):
        ifc.get_entity("obj").should_be_called().will_return("element")
        ifc.run("attribute.edit_attributes", product="element", attributes={"name": "value"}).should_be_called()
        subject.copy_attribute_to_selection(ifc, name="name", value="value", obj="obj")

    def test_do_nothing_if_object_is_not_an_element(self, ifc):
        ifc.get_entity("obj").should_be_called().will_return(None)
        subject.copy_attribute_to_selection(ifc, name="name", value="value", obj="obj")

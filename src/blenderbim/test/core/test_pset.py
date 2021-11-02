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

import blenderbim.core.pset as subject
from test.core.bootstrap import ifc, pset


class TestCopyPropertyToSelection:
    def test_doing_nothing_if_object_is_not_an_element(self, ifc, pset):
        ifc.get_entity("obj").should_be_called().will_return(None)
        subject.copy_property_to_selection(
            ifc, pset, obj="obj", pset_name="pset_name", prop_name="prop_name", prop_value="prop_value"
        )

    def test_copying_the_property_to_an_existing_pset(self, ifc, pset):
        ifc.get_entity("obj").should_be_called().will_return("element")
        pset.get_element_pset("element", "pset_name").should_be_called().will_return("pset")
        ifc.run("pset.edit_pset", pset="pset", properties={"prop_name": "prop_value"}).should_be_called()
        subject.copy_property_to_selection(
            ifc, pset, obj="obj", pset_name="pset_name", prop_name="prop_name", prop_value="prop_value"
        )

    def test_creating_a_new_pset_if_it_doesnt_exist(self, ifc, pset):
        ifc.get_entity("obj").should_be_called().will_return("element")
        pset.get_element_pset("element", "pset_name").should_be_called().will_return(None)
        ifc.run("pset.add_pset", product="element", name="pset_name").should_be_called().will_return("pset")
        ifc.run("pset.edit_pset", pset="pset", properties={"prop_name": "prop_value"}).should_be_called()
        subject.copy_property_to_selection(
            ifc, pset, obj="obj", pset_name="pset_name", prop_name="prop_name", prop_value="prop_value"
        )

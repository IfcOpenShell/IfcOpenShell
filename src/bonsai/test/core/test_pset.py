# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bonsai.core.pset as subject
from test.core.bootstrap import ifc, pset


class TestCopyPropertyToSelection:
    def test_doing_nothing_if_object_is_not_an_element(self, ifc, pset):
        ifc.get_entity("obj").should_be_called().will_return(None)
        subject.copy_property_to_selection(
            ifc, pset, is_pset=True, obj="obj", pset_name="pset_name", prop_name="prop_name", prop_value="prop_value"
        )

    def test_copying_the_property_to_an_existing_pset(self, ifc, pset):
        ifc.get_entity("obj").should_be_called().will_return("element")
        pset.get_element_pset("element", "pset_name").should_be_called().will_return("pset")
        ifc.run("pset.edit_pset", pset="pset", properties={"prop_name": "prop_value"}).should_be_called()
        subject.copy_property_to_selection(
            ifc, pset, is_pset=True, obj="obj", pset_name="pset_name", prop_name="prop_name", prop_value="prop_value"
        )

    def test_creating_a_new_pset_if_it_doesnt_exist(self, ifc, pset):
        ifc.get_entity("obj").should_be_called().will_return("element")
        pset.get_element_pset("element", "pset_name").should_be_called().will_return(None)
        ifc.run("pset.add_pset", product="element", name="pset_name").should_be_called().will_return("pset")
        ifc.run("pset.edit_pset", pset="pset", properties={"prop_name": "prop_value"}).should_be_called()
        subject.copy_property_to_selection(
            ifc, pset, is_pset=True, obj="obj", pset_name="pset_name", prop_name="prop_name", prop_value="prop_value"
        )

    def test_copying_the_quantity_to_an_existing_qto(self, ifc, pset):
        ifc.get_entity("obj").should_be_called().will_return("element")
        pset.get_element_pset("element", "qto_name").should_be_called().will_return("qto")
        ifc.run("pset.edit_qto", qto="qto", properties={"prop_name": "prop_value"}).should_be_called()
        subject.copy_property_to_selection(
            ifc, pset, is_pset=False, obj="obj", pset_name="qto_name", prop_name="prop_name", prop_value="prop_value"
        )

    def test_creating_a_new_qto_if_it_doesnt_exist(self, ifc, pset):
        ifc.get_entity("obj").should_be_called().will_return("element")
        pset.get_element_pset("element", "qto_name").should_be_called().will_return(None)
        ifc.run("pset.add_qto", product="element", name="qto_name").should_be_called().will_return("qto")
        ifc.run("pset.edit_qto", qto="qto", properties={"prop_name": "prop_value"}).should_be_called()
        subject.copy_property_to_selection(
            ifc, pset, is_pset=False, obj="obj", pset_name="qto_name", prop_name="prop_name", prop_value="prop_value"
        )


class TestUnsharePset:
    def test_run(self, ifc, pset):
        ifc.get_entity_by_id("pset_id").should_be_called().will_return("pset")
        pset.get_selected_pset_elements("obj_name", "obj_type", "pset").should_be_called().will_return("elements")
        ifc.run("pset.unshare_pset", products="elements", pset="pset").should_be_called()
        subject.unshare_pset(ifc, pset, "obj_type", "obj_name", "pset_id")

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

import bonsai.core.attribute as subject
from test.core.bootstrap import ifc, blender, root, spatial


class TestCopyAttributeToSelection:
    def test_run(self, ifc, blender, root, spatial):
        blender.get_selected_objects(include_active=False).should_be_called().will_return(["obj"])
        ifc.get_entity("obj").should_be_called().will_return("element")
        ifc.run("attribute.edit_attributes", product="element", attributes={"name": "value"}).should_be_called()
        assert subject.copy_attribute_to_selection(ifc, blender, root, spatial, name="name", value="value") == 1

    def test_do_nothing_if_object_is_not_an_element(self, ifc, blender, root, spatial):
        blender.get_selected_objects(include_active=False).should_be_called().will_return(["obj"])
        ifc.get_entity("obj").should_be_called().will_return(None)
        assert subject.copy_attribute_to_selection(ifc, blender, root, spatial, name="name", value="value") == 0

    def test_changing_object_name_in_blender_if_attribute_changed(self, ifc, blender, root, spatial):
        blender.get_selected_objects(include_active=False).should_be_called().will_return(["obj"])
        ifc.get_entity("obj").should_be_called().will_return("element")
        ifc.run("attribute.edit_attributes", product="element", attributes={"Name": "value"}).should_be_called()
        root.set_object_name("obj", "element").should_be_called()
        root.is_spatial_element("element").should_be_called().will_return(False)
        assert subject.copy_attribute_to_selection(ifc, blender, root, spatial, name="Name", value="value") == 1

    def test_refreshing_spatial_decomposition_if_identification_changed(self, ifc, blender, root, spatial):
        blender.get_selected_objects(include_active=False).should_be_called().will_return(["obj"])
        ifc.get_entity("obj").should_be_called().will_return("element")
        ifc.run("attribute.edit_attributes", product="element", attributes={"Name": "value"}).should_be_called()
        root.set_object_name("obj", "element").should_be_called()
        root.is_spatial_element("element").should_be_called().will_return(True)
        spatial.import_spatial_decomposition().should_be_called()
        assert subject.copy_attribute_to_selection(ifc, blender, root, spatial, name="Name", value="value") == 1

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

import blenderbim.core.type as subject
from test.core.bootstrap import ifc, type


class TestAssignType:
    def test_assigning_and_switching_to_an_existing_type_data(self, ifc, type):
        ifc.run("type.assign_type", related_object="element", relating_type="type").should_be_called()
        type.has_material_usage("element").should_be_called().will_return(False)
        ifc.get_object("type").should_be_called().will_return("type_obj")
        type.get_object_data("type_obj").should_be_called().will_return("type_obj_data")
        type.change_object_data("obj", "type_obj_data", is_global=False).should_be_called()
        ifc.get_object("element").should_be_called().will_return("obj")
        type.disable_editing("obj").should_be_called()
        subject.assign_type(ifc, type, element="element", type="type")

    def test_assigning_and_not_changing_data_if_the_type_has_no_data(self, ifc, type):
        ifc.run("type.assign_type", related_object="element", relating_type="type").should_be_called()
        type.has_material_usage("element").should_be_called().will_return(False)
        ifc.get_object("type").should_be_called().will_return("type_obj")
        type.get_object_data("type_obj").should_be_called().will_return(None)
        ifc.get_object("element").should_be_called().will_return("obj")
        type.disable_editing("obj").should_be_called()
        subject.assign_type(ifc, type, element="element", type="type")

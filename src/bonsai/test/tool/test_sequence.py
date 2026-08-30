# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.pset
import ifcopenshell.api.root

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.sequence import Sequence as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Sequence)


class TestGetElementStatus(NewFile):
    def test_common_pset(self):
        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}

    def test_epset(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "EPset_Status")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}


class TestSetVisibilityByStatus(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        def add_wall_with_status(status):
            bpy.ops.mesh.primitive_cube_add()
            obj = bpy.context.active_object
            bpy.ops.bim.assign_class(ifc_class="IfcWall")
            if status is not None:
                element = tool.Ifc.get_entity(obj)
                pset = ifcopenshell.api.pset.add_pset(ifc, element, "Pset_WallCommon")
                ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": [status]})
            return obj

        obj_new = add_wall_with_status("NEW")
        obj_existing = add_wall_with_status("EXISTING")
        obj_no_status = add_wall_with_status(None)

        subject.set_visibility_by_status({"NEW"})
        assert obj_new.hide_get() is False
        assert obj_existing.hide_get() is True
        assert obj_no_status.hide_get() is True

        subject.set_visibility_by_status({"No Status", "EXISTING"})
        assert obj_new.hide_get() is True
        assert obj_existing.hide_get() is False
        assert obj_no_status.hide_get() is False


class TestEnableStatusFilters(NewFile):
    def test_has_elements_is_stored_on_the_status_property(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        bpy.ops.bim.assign_class(ifc_class="IfcWall")
        element = tool.Ifc.get_entity(obj)
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["NEW"]})

        bpy.ops.bim.enable_status_filters()

        statuses_by_name = {s.name: s for s in tool.Sequence.get_status_props().statuses}
        assert statuses_by_name["NEW"].has_elements is True
        assert statuses_by_name["EXISTING"].has_elements is False


class TestAssignStatus(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.assign_status(status="NEW")
        assert subject.get_element_status(element) == {"NEW"}

        bpy.ops.bim.assign_status(status="EXISTING")
        assert subject.get_element_status(element) == {"EXISTING"}

        bpy.ops.bim.assign_status(status="EXISTING", should_unassign_status=True)
        assert subject.get_element_status(element) == set()

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


import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.sequence import Sequence as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Sequence)


class TestApplyVisibilityToVoids(NewFile):
    def create_wall_with_opening(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add(size=2)
        bpy.ops.bim.assign_class(ifc_class="IfcWall")
        wall_obj = bpy.data.objects["IfcWall/Cube"]
        bpy.ops.mesh.primitive_cube_add(size=1)
        opening_obj = bpy.context.active_object
        wall_obj.select_set(True)
        opening_obj.select_set(True)
        bpy.context.view_layer.objects.active = wall_obj
        bpy.ops.bim.add_opening()
        wall = tool.Ifc.get_entity(wall_obj)
        opening = wall.HasOpenings[0].RelatedOpeningElement
        return wall_obj, wall, opening

    def test_hiding_an_opening_recuts_the_host_without_modifying_the_model(self):
        wall_obj, wall, opening = self.create_wall_with_opening()
        ifc = tool.Ifc.get()
        cut_vertices = len(wall_obj.data.vertices)
        ifc_before = ifc.to_string()

        subject.apply_visibility_to_voids({wall})
        assert len(wall_obj.data.vertices) < cut_vertices
        assert opening.Representation
        assert ifc.to_string() == ifc_before

        subject.apply_visibility_to_voids({wall, opening})
        assert len(wall_obj.data.vertices) == cut_vertices
        assert ifc.to_string() == ifc_before

    def test_geometry_file_has_hidden_openings_without_representation(self):
        _, wall, opening = self.create_wall_with_opening()
        ifc = tool.Ifc.get()
        assert subject.get_geometry_file(ifc, [wall]) is ifc

        subject.apply_visibility_to_voids({wall})
        geometry_file = subject.get_geometry_file(ifc, [wall])
        assert geometry_file is not ifc
        assert geometry_file.by_id(opening.id()).Representation is None
        assert opening.Representation

        subject.apply_visibility_to_voids({wall, opening})
        assert subject.get_geometry_file(ifc, [wall]) is ifc


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

# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Bonsai contributors
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

# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell

import bonsai.tool as tool
from bonsai.tool.model import Model as subject
from test.bim.bootstrap import NewFile


class TestApplyIfcMaterialChangesToleratesStaleIfcDefinitionId(NewFile):
    def test_run(self):
        from unittest import mock

        ifc_file = ifcopenshell.file()
        tool.Ifc.set(ifc_file)
        element = ifc_file.createIfcWall()
        representation = ifc_file.createIfcShapeRepresentation()
        obj = bpy.data.objects.new("Object", (mesh := bpy.data.meshes.new("Mesh")))
        tool.Ifc.link(element, obj)
        stale_id = representation.id()
        tool.Geometry.get_mesh_props(mesh).ifc_definition_id = stale_id
        ifc_file.remove(representation)

        with mock.patch("bonsai.core.geometry.switch_representation") as switch_representation:
            subject.apply_ifc_material_changes([element])
        switch_representation.assert_not_called()

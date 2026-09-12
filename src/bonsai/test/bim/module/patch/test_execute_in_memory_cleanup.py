# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
#
# This file was generated with the assistance of an AI coding tool.

import tempfile
from pathlib import Path

import bpy
import ifcopenshell
import ifcopenshell.api.document
import pytest

import bonsai.core.drawing
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.patch


def add_object(ifc_class: str) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    bpy.ops.bim.assign_class(ifc_class=ifc_class)
    assert tool.Ifc.get_entity(obj).is_a(ifc_class)
    return obj


def execute_patch_in_memory(recipe: str, tmpdir: str) -> None:
    props = tool.Patch.get_patch_props()
    props.should_load_from_memory = True
    props.ifc_patch_recipes = recipe
    props.ifc_patch_output = str(Path(tmpdir) / f"{recipe}.ifc")
    assert bpy.ops.bim.execute_ifc_patch() == {"FINISHED"}


class TestExecuteIfcPatchInMemoryCleanup(NewIfc):
    """A recipe run on the loaded model changes the IFC file behind Bonsai's
    back. Blender objects, element maps and open document lists that still
    refer to deleted elements or old GlobalIds must be brought back in line,
    or saving the project fails with 'Instance #N not found'."""

    def test_objects_of_deleted_elements_are_removed_and_project_saves(self):
        ifc = tool.Ifc.get()
        wall_type = add_object("IfcWallType")
        wall = add_object("IfcWall")

        with tempfile.TemporaryDirectory() as tmpdir:
            execute_patch_in_memory("PurgeData", tmpdir)

            assert not ifc.by_type("IfcTypeObject"), "PurgeData should have removed the wall type"
            assert not tool.Blender.is_valid_data_block(wall_type)
            assert tool.Blender.is_valid_data_block(wall)
            assert all(tool.Ifc.get_entity_by_id(i) for i in IfcStore.id_map)

            output_path = Path(tmpdir) / "saved.ifc"
            assert bpy.ops.bim.save_project(filepath=str(output_path), should_save_as=True) == {"FINISHED"}
            assert output_path.exists()

    def test_open_document_lists_are_reloaded(self):
        ifc = tool.Ifc.get()
        for scope in ("SHEET", "SCHEDULE", "REFERENCE"):
            information = ifcopenshell.api.document.add_information(ifc)
            information.Scope = scope
            information.Name = scope
        bonsai.core.drawing.load_sheets(tool.Drawing)
        bonsai.core.drawing.load_schedules(tool.Drawing)
        bonsai.core.drawing.load_references(tool.Drawing)
        props = tool.Drawing.get_document_props()
        assert (len(props.sheets), len(props.schedules), len(props.references)) == (1, 1, 1)

        with tempfile.TemporaryDirectory() as tmpdir:
            execute_patch_in_memory("PurgeData", tmpdir)

        assert not ifc.by_type("IfcDocumentInformation"), "PurgeData should have removed the documents"
        assert (len(props.sheets), len(props.schedules), len(props.references)) == (0, 0, 0)

    def test_element_maps_follow_regenerated_global_ids(self):
        wall = add_object("IfcWall")
        element = tool.Ifc.get_entity(wall)
        old_global_id = element.GlobalId

        with tempfile.TemporaryDirectory() as tmpdir:
            execute_patch_in_memory("RegenerateGlobalIds", tmpdir)

        assert element.GlobalId != old_global_id
        assert IfcStore.id_map[element.id()] == wall
        assert IfcStore.guid_map.get(element.GlobalId) == wall
        assert old_global_id not in IfcStore.guid_map

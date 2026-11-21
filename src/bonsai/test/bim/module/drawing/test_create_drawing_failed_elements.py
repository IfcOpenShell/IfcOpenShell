# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

from pathlib import Path

import bpy
import pytest

import bonsai.tool as tool
from bonsai.bim.module.drawing.operator import CreateDrawing
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.drawing


class FailingSerialiser:
    def __init__(self, serialiser, failing_guid, failed_writes):
        self.serialiser = serialiser
        self.failing_guid = failing_guid
        self.failed_writes = failed_writes

    def write(self, elem):
        if elem.guid == self.failing_guid:
            self.failed_writes.append(elem.guid)
            raise RuntimeError("Standard_ConstructionError")
        self.serialiser.write(elem)

    def __getattr__(self, name):
        return getattr(self.serialiser, name)


def add_wall(location):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    bpy.ops.bim.assign_class(ifc_class="IfcWall", predefined_type="SOLIDWALL", userdefined_type="")
    return tool.Ifc.get_entity(bpy.context.active_object)


class TestCreateDrawingWithAFailingElement(NewFile):
    def test_the_failing_element_is_skipped_and_reported_and_the_rest_is_drawn(self, monkeypatch, capfd):
        bpy.ops.bim.create_project()
        tool.Project.save_test_project()
        good_wall = add_wall((0, 0, 0))
        bad_wall = add_wall((3, 0, 0))

        props = tool.Drawing.get_document_props()
        bpy.ops.bim.load_drawings()
        for item in props.drawings:
            item.is_expanded = True
        bpy.ops.bim.add_drawing()
        drawing = next(e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING")
        props.active_drawing_index = next(
            i for i, item in enumerate(props.drawings) if item.ifc_definition_id == drawing.id()
        )
        bpy.ops.bim.activate_drawing(drawing=drawing.id())

        failed_writes = []
        setup_serialiser = CreateDrawing.setup_serialiser

        def setup_failing_serialiser(operator, target_view):
            setup_serialiser(operator, target_view)
            operator.serialiser = FailingSerialiser(operator.serialiser, bad_wall.GlobalId, failed_writes)

        monkeypatch.setattr(CreateDrawing, "setup_serialiser", setup_failing_serialiser)
        capfd.readouterr()
        bpy.ops.bim.create_drawing()

        svg = (Path(tool.Ifc.get_path()).parent / "drawings" / f"{drawing.Name}.svg").read_text()
        assert f'ifc:guid="{good_wall.GlobalId}"' in svg
        assert f'ifc:guid="{bad_wall.GlobalId}"' not in svg
        assert failed_writes == [bad_wall.GlobalId]
        assert f"IfcWall {bad_wall.GlobalId} (Standard_ConstructionError)" in capfd.readouterr().out

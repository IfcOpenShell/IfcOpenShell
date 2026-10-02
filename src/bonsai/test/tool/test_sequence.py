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


class TestAddTextAnimationHandler(NewFile):
    def test_timeline_text_uses_the_sequence_date_format(self):
        tool.Ifc.set(ifcopenshell.file())
        props = subject.get_work_schedule_props()
        props.visualisation_start = "2026-03-05"
        props.visualisation_finish = "2026-06-15"
        handlers = list(bpy.app.handlers.frame_change_post)
        try:
            subject.add_text_animation_handler({"start_frame": 1, "total_frames": 100})
            bpy.context.scene.frame_set(1)
            assert bpy.data.curves["Timeline"].body == "05/03/26"
        finally:
            for handler in list(bpy.app.handlers.frame_change_post):
                if handler not in handlers:
                    bpy.app.handlers.frame_change_post.remove(handler)


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

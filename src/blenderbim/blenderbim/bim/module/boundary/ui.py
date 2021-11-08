# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.boundary.data import Data


class BIM_PT_SceneBoundaries(Panel):
    bl_label = "IFC Space Boundaries"
    bl_id_name = "BIM_PT_scene_boundaries"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        row = self.layout.row()
        row.operator("bim.load_project_space_boundaries")
        row.operator("bim.select_project_space_boundaries", text="", icon="RESTRICT_SELECT_OFF")


class BIM_PT_Boundary(Panel):
    bl_label = "IFC Space Boundaries"
    bl_idname = "BIM_PT_Boundary"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if IfcStore.get_file().by_id(props.ifc_definition_id).is_a() not in ["IfcSpace", "IfcExternalSpatialElement"]:
            return False
        return True

    def draw(self, context):
        self.oprops = context.active_object.BIMObjectProperties
        row = self.layout.row()
        row.operator("bim.load_space_boundaries")
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        for boundary_id in Data.spaces.get(self.oprops.ifc_definition_id, []):
            boundary = Data.boundaries[boundary_id]
            row = self.layout.row()
            row.label(text=f"{boundary_id}", icon="GHOST_ENABLED")
            op = row.operator("bim.load_boundary", text="", icon="RESTRICT_SELECT_OFF")
            op.boundary_id = boundary_id


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

from bpy.types import Panel
from ifcopenshell.api.context.data import Data
from blenderbim.bim.ifc import IfcStore


class BIM_PT_context(Panel):
    bl_label = "IFC Geometric Representation Contexts"
    bl_idname = "BIM_PT_context"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        props = context.scene.BIMProperties

        row = self.layout.row(align=True)
        row.prop(props, "available_contexts", text="")
        row.prop(props, "available_subcontexts", text="")
        row.prop(props, "available_target_views", text="")
        row.operator("bim.add_subcontext", icon="ADD", text="")

        for ifc_definition_id, context in Data.contexts.items():
            box = self.layout.box()
            row = box.row(align=True)
            row.label(text=context["ContextType"])
            row.operator("bim.remove_subcontext", icon="X", text="").ifc_definition_id = ifc_definition_id
            for ifc_definition_id2, subcontext in context["HasSubContexts"].items():
                row = box.row(align=True)
                row.label(text=subcontext["ContextType"])
                row.label(text=subcontext["ContextIdentifier"])
                row.label(text=subcontext["TargetView"])
                row.operator("bim.remove_subcontext", icon="X", text="").ifc_definition_id = ifc_definition_id2

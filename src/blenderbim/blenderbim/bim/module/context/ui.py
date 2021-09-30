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
import blenderbim.tool as tool
from blenderbim.bim.module.context.data import ContextData


class BIM_PT_context(bpy.types.Panel):
    bl_label = "IFC Geometric Representation Contexts"
    bl_idname = "BIM_PT_context"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not ContextData.is_loaded:
            ContextData.load()

        props = context.scene.BIMContextProperties

        row = self.layout.row(align=True)
        row.prop(props, "contexts", text="")
        row.prop(props, "subcontexts", text="")
        row.prop(props, "target_views", text="")
        op = row.operator("bim.add_subcontext", icon="ADD", text="")
        op.context = props.contexts
        op.subcontext = props.subcontexts
        op.target_view = props.target_views

        for context in ContextData.data["contexts"]:
            box = self.layout.box()
            row = box.row(align=True)
            row.label(text=context["context_type"])
            row.operator("bim.remove_subcontext", icon="X", text="").context = context["id"]
            for subcontext in context["subcontexts"]:
                row = box.row(align=True)
                row.label(text=subcontext["context_type"])
                row.label(text=subcontext["context_identifier"])
                row.label(text=subcontext["target_view"])
                row.operator("bim.remove_subcontext", icon="X", text="").context = subcontext["id"]

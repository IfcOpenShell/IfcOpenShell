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
import blenderbim.tool as tool
from blenderbim.bim.module.context.data import ContextData


class BIM_PT_context(bpy.types.Panel):
    bl_label = "Geometric Representation Contexts"
    bl_idname = "BIM_PT_context"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_geometry"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not ContextData.is_loaded:
            ContextData.load()

        props = context.scene.BIMContextProperties

        row = self.layout.row(align=True)
        row.prop(props, "contexts", text="")
        op = row.operator("bim.add_context", icon="ADD", text="")
        op.context_type = props.contexts
        op.context_identifier = ""
        op.target_view = ""
        op.parent = 0

        for ifc_context in ContextData.data["contexts"]:
            box = self.layout.box()

            if ifc_context["is_editing"]:
                row = box.row(align=True)
                row.operator("bim.edit_context", icon="CHECKMARK")
                row.operator("bim.disable_editing_context", icon="CANCEL", text="")
                blenderbim.bim.helper.draw_attributes(ifc_context["props"], box)
            else:
                row = box.row(align=True)
                row.label(text=ifc_context["context_type"])
                row.operator("bim.enable_editing_context", icon="GREASEPENCIL", text="").context = ifc_context["id"]
                row.operator("bim.remove_context", icon="X", text="").context = ifc_context["id"]

            row = box.row(align=True)
            blenderbim.bim.helper.prop_with_search(row, props, "subcontexts", text="")
            blenderbim.bim.helper.prop_with_search(row, props, "target_views", text="")
            op = row.operator("bim.add_context", icon="ADD", text="")
            op.context_type = ifc_context["context_type"]
            op.context_identifier = props.subcontexts
            op.target_view = props.target_views
            op.parent = ifc_context["id"]

            for subcontext in ifc_context["subcontexts"]:
                if subcontext["is_editing"]:
                    row = box.row(align=True)
                    row.operator("bim.edit_context", icon="CHECKMARK")
                    row.operator("bim.disable_editing_context", icon="CANCEL", text="")
                    blenderbim.bim.helper.draw_attributes(subcontext["props"], box)
                else:
                    row = box.row(align=True)
                    row.label(text=subcontext["context_type"])
                    row.label(text=subcontext["context_identifier"])
                    row.label(text=subcontext["target_view"])
                    row.operator("bim.enable_editing_context", icon="GREASEPENCIL", text="").context = subcontext["id"]
                    row.operator("bim.remove_context", icon="X", text="").context = subcontext["id"]

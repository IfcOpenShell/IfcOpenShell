# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

from bpy.types import Panel, UIList, Mesh
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.layer.data import LayersData


class BIM_PT_layers(Panel):
    bl_label = "Presentation Layers"
    bl_idname = "BIM_PT_layers"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_geometric_relationships"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not LayersData.is_loaded:
            LayersData.load()

        self.props = context.scene.BIMLayerProperties

        row = self.layout.row(align=True)
        row.label(text=f"{LayersData.data['total_layers']} Layers Found")
        if self.props.is_editing:
            row.operator("bim.add_presentation_layer", text="", icon="ADD")
            row.operator("bim.disable_layer_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_layers", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_layers",
                "",
                self.props,
                "layers",
                self.props,
                "active_layer_index",
            )

        if self.props.active_layer_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.layer_attributes:
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_layers(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)

            if context.active_object and isinstance(context.active_object.data, Mesh):
                mprops = context.active_object.data.BIMMeshProperties
                if item.ifc_definition_id in LayersData.data["active_layers"]:
                    op = row.operator("bim.unassign_presentation_layer", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.layer = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_presentation_layer", text="", icon="KEYFRAME", emboss=False)
                    op.layer = item.ifc_definition_id

            # TODO: replace placeholder UI for hiding presentation layers
            row.operator("bim.disable_editing_layer", text="", icon="HIDE_OFF", emboss=False)
            row.operator("bim.disable_editing_layer", text="", icon="FREEZE", emboss=False)

            if context.scene.BIMLayerProperties.active_layer_id == item.ifc_definition_id:
                op = row.operator("bim.select_layer_products", text="", icon="RESTRICT_SELECT_OFF")
                op.layer = item.ifc_definition_id
                row.operator("bim.edit_presentation_layer", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_layer", text="", icon="CANCEL")
            elif context.scene.BIMLayerProperties.active_layer_id:
                op = row.operator("bim.select_layer_products", text="", icon="RESTRICT_SELECT_OFF")
                op.layer = item.ifc_definition_id
                row.operator("bim.remove_presentation_layer", text="", icon="X").layer = item.ifc_definition_id
            else:
                op = row.operator("bim.select_layer_products", text="", icon="RESTRICT_SELECT_OFF")
                op.layer = item.ifc_definition_id
                op = row.operator("bim.enable_editing_layer", text="", icon="GREASEPENCIL")
                op.layer = item.ifc_definition_id
                row.operator("bim.remove_presentation_layer", text="", icon="X").layer = item.ifc_definition_id

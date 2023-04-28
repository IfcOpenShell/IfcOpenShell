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
from blenderbim.bim.module.qto.data import QtoData


class BIM_PT_qto_utilities(bpy.types.Panel):
    bl_idname = "BIM_PT_qto_utilities"
    bl_label = "Quantity Take-off"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        if not QtoData.is_loaded:
            QtoData.load()

        layout = self.layout
        props = context.scene.BIMQtoProperties

        row = layout.row()
        row.prop(props, "qto_result", text="Results")

        row = layout.row(align=True)
        row.operator("bim.calculate_circle_radius")
        row = layout.row(align=True)
        row.operator("bim.calculate_edge_lengths")
        row = layout.row(align=True)
        row.operator("bim.calculate_face_areas")
        row = layout.row(align=True)
        row.operator("bim.calculate_object_volumes")

        row = layout.row(align=True)
        row.prop(props, "qto_methods", text="")
        row.operator("bim.execute_qto_method", icon="PROPERTIES", text="")

        row = layout.row(align=True)
        row.prop(props, "qto_name", text="")
        row.prop(props, "prop_name", text="")
        row.operator("bim.quantify_objects", icon="COPYDOWN", text="")

        row = layout.row(align=True)
        row.operator("bim.assign_objects_base_qto")

        row = layout.row(align=True)
        row.operator("bim.calculate_all_quantities", icon="MOD_EDGESPLIT")

        if context.selected_objects:
            row = layout.row(align=True)
            row.label(text=f"Relating Cost Item:")

            if QtoData.data['has_cost_item']:
                for relating_cost_item in QtoData.data['relating_cost_items']:
                    row.label(text=f"\n")
                    row = layout.row(align=True)
                    row.label(text=f"Cost item name:")
                    row.label(text=f"{relating_cost_item['cost_item_name']}")
                    row = layout.row(align=True)
                    row.label(text=f"Quantity name:")
                    row.label(text=f"{relating_cost_item['quantity_name']}")
                    row = layout.row(align=True)
                    row.label(text=f"Quantity value:")
                    row.label(text=f"{relating_cost_item['quantity_value']}")
                    row = layout.row(align=True)
                    row.label(text=f"Quantity type:")
                    row.label(text=f"{relating_cost_item['quantity_type']}")
                    row = layout.row(align=True)
            else:
                row = layout.row(align=True)
                row.label(text = f"No cost item related")


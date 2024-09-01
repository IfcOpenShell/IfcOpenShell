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


import bpy
import json
import os

with open(os.path.join(os.path.dirname(__file__), "spectraldb.json"), "r") as f:
    spectraldb = json.load(f)


class MATERIAL_UL_radiance_materials(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)

            # Adding color preview or glass icon
            if item.category == "Glass":
                row.label(icon="SHADING_TEXTURE")
            else:
                color_rect = row.row()
                color_rect.prop(item, "color", text="")
                color_rect.scale_x = 0.3

            row.prop(item, "name", text="", emboss=False, icon_value=icon)
            if item.is_mapped:
                row.label(text=f"{item.category} - {item.subcategory}")
                op = row.operator("bim.unmap_material", text="", icon="X")
                op.material_index = index
            else:
                row.label(text="Not Mapped (White)")

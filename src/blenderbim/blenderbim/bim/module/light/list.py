import bpy
import json
import os

with open(os.path.join(os.path.dirname(__file__), "spectraldb.json"), "r") as f:
    spectraldb = json.load(f)


class MATERIAL_UL_radiance_materials(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon_value=icon)
            if item.is_mapped:
                row.label(text=f"{item.category} - {item.subcategory}")
                op = row.operator("bim.unmap_material", text="", icon="X")
                op.material_index = index
            else:
                row.label(text="Not Mapped (White)")

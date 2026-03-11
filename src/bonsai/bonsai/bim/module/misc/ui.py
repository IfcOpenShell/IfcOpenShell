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

import bonsai.tool as tool


class BIM_PT_misc_utilities(bpy.types.Panel):
    bl_idname = "BIM_PT_misc_utilities"
    bl_label = "Miscellaneous"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_sandbox"

    def draw(self, context):
        layout = self.layout
        assert layout
        props = tool.Misc.get_misc_props()
        row = layout.split(factor=0.2, align=True)
        row.prop(props, "override_colour", text="")
        row.operator("bim.set_override_colour")
        row = layout.row()
        row.operator("bim.snap_spaces_together")
        row = layout.split(factor=0.2, align=True)
        row.prop(props, "total_storeys", text="")
        row.operator("bim.resize_to_storey").total_storeys = props.total_storeys
        row = layout.row(align=True)
        row.operator("bim.split_along_edge", text="Split Along Edge").mode = "BOOLEAN"
        row.operator("bim.split_along_edge", text="Bisect At Faces").mode = "BISECT"
        row = layout.row()
        row.operator("bim.get_connected_system_elements")
        row = layout.row()
        row.operator("bim.draw_system_arrows")
        row = layout.row()
        row.operator("bim.clean_wireframes")
        row = layout.row()
        row.operator("bim.patch_non_parametric_mep_segment")
        row = layout.row(align=True)
        row.operator("bim.enable_editing_sketch_extrusion_profile", text="Start Sketching")
        row.operator("bim.edit_sketch_extrusion_profile", text="", icon="FILE_REFRESH")
        row.operator("bim.disable_editing_sketch_extrusion_profile", text="", icon="CANCEL")
        row = layout.row()
        row.operator("bim.import_plot", text="Import Plot Coordinates", icon="FILE_FOLDER")


class BIM_PT_quick_favorites_manager(bpy.types.Panel):
    bl_idname = "BIM_PT_quick_favorites_manager"
    bl_label = "Quick Favorites Manager"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_sandbox"

    def draw(self, context):
        layout = self.layout
        assert layout
        props = tool.Misc.get_misc_props()

        row = layout.row(align=True)
        row.label(text="Quick Favorites:")
        row.operator("bim.add_quick_favorites_item", text="", icon="ADD")
        row.operator("bim.import_quick_favorites", text="", icon="BLENDER")
        op = row.operator("bim.show_description", text="", icon="INFO")
        op.attr_name = "Quick Favorites Manager"
        op.description = (
            "Blender does not support editing Quick Favorites natively. "
            "This manager allows you to load existing Quick Favorites operators, "
            "configure their properties and labels, and re-add them to the menu with customized settings."
        )

        for fav in props.quick_favorites:
            if fav.operator_id:
                row = layout.row()
                op = row.operator(fav.operator_id, text=fav.label)
                for item in fav.properties:
                    if item.is_active:
                        setattr(op, item.name, getattr(item, item.value_prop))

        layout.separator()

        for i, fav in enumerate(props.quick_favorites):
            box = layout.box()
            row = box.row(align=True)
            row.prop(fav, "is_expanded", text="", icon="TRIA_DOWN" if fav.is_expanded else "TRIA_RIGHT", emboss=False)
            row.prop(fav, "label", text="")
            if i > 0:
                up = row.operator("bim.move_quick_favorites_item", text="", icon="TRIA_UP")
                up.index = i
                up.direction = "UP"
            if i < len(props.quick_favorites) - 1:
                down = row.operator("bim.move_quick_favorites_item", text="", icon="TRIA_DOWN")
                down.index = i
                down.direction = "DOWN"
            row.operator("bim.remove_quick_favorites_item", text="", icon="X").index = i
            if not fav.is_expanded:
                continue
            row = box.row(align=True)
            row.prop(fav, "search", text="")
            row.operator("bim.confirm_quick_favorite_operator", text="", icon="VIEWZOOM").index = i
            if not fav.operator_id:
                continue
            layout.separator()
            if fav.properties:
                box.label(text="Properties:")
                prop_box = box.box()
                for item in fav.properties:
                    row = prop_box.row(align=True)
                    row.prop(item, item.value_prop, text=item.display_name)
                    row.prop(item, "is_active", text="", icon="RADIOBUT_ON" if item.is_active else "RADIOBUT_OFF")
            else:
                box.label(text="No Properties.")

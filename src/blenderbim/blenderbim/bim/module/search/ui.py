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
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_search(Panel):
    bl_label = "IFC Search"
    bl_idname = "BIM_PT_search"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        props = context.scene.BIMSearchProperties

        row = self.layout.row()
        row.prop(props, "should_use_regex")
        row = self.layout.row()
        row.prop(props, "should_ignorecase")

        row = self.layout.row(align=True)
        row.operator("bim.reset_object_colours", icon="BRUSH_DATA")

        row = self.layout.row(align=True)
        row.prop(props, "global_id", text="", icon="TRACKER")
        row.operator("bim.select_global_id", text="", icon="VIEWZOOM").global_id = props.global_id

        row = self.layout.row(align=True)
        row.prop(props, "ifc_class", text="", icon="OBJECT_DATA")
        row.operator("bim.select_ifc_class", text="", icon="VIEWZOOM").ifc_class = props.ifc_class
        row.operator("bim.colour_by_class", text="", icon="BRUSH_DATA")

        row = self.layout.row(align=True)
        row.prop(props, "search_attribute_name", text="", icon="PROPERTIES")
        row.prop(props, "search_attribute_value", text="")
        row.operator("bim.select_attribute", text="", icon="VIEWZOOM")
        row.operator("bim.colour_by_attribute", text="", icon="BRUSH_DATA")

        row = self.layout.row(align=True)
        row.prop(props, "search_pset_name", text="", icon="COPY_ID")
        row.prop(props, "search_prop_name", text="")
        row.prop(props, "search_pset_value", text="")
        row.operator("bim.select_pset", text="", icon="VIEWZOOM")
        row.operator("bim.colour_by_pset", text="", icon="BRUSH_DATA")

        row = self.layout.row(align=True)
        row.operator("bim.activate_ifc_type_filter", icon="FILTER")


class BIM_UL_ifctype_filter(bpy.types.UIList):
    "This UI List is to list out all the selected IfcType and number of it as well as providing the BoolProperty to select/deselect"
    use_filter_linked: bpy.props.BoolProperty(name="Included", default=True, options=set(), description="Filter")

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout
        split.use_property_split = True
        split.use_property_decorate = False
        split.prop(
            item, "is_selected", text="", emboss=False, icon="CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT"
        )
        split.prop(item, "name", text="", emboss=False, slider=True)
        split = split.column()
        split.scale_x = 0.5
        split.label(text=str(item.total))

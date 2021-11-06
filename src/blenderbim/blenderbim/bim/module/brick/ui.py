# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from bpy.types import Panel, UIList
from blenderbim.bim.module.brick.data import BrickschemaData


class BIM_PT_brickschema(Panel):
    bl_label = "Brickschema Project"
    bl_idname = "BIM_PT_brickschema"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        if not BrickschemaData.is_loaded:
            BrickschemaData.load()
        self.props = context.scene.BIMBrickProperties

        if not BrickschemaData.data["is_loaded"]:
            row = self.layout.row()
            row.operator("bim.load_brick_project")
            return

        row = self.layout.row(align=True)
        if len(self.props.brick_breadcrumbs):
            row.operator("bim.rewind_brick_class", text="", icon="FRAME_PREV")
        row.label(text=self.props.active_brick_class)
        row.operator("bim.close_brick_project", text="", icon="CANCEL")

        self.layout.template_list("BIM_UL_bricks", "", self.props, "bricks", self.props, "active_brick_index")

        for attribute in BrickschemaData.data["attributes"]:
            row = self.layout.row(align=True)
            row.label(text=attribute["name"])
            row.label(text=attribute["value"])
            if attribute["is_uri"]:
                op = row.operator("bim.view_brick_item", text="", icon="DISCLOSURE_TRI_RIGHT")
                op.item = attribute["value_uri"]


class BIM_UL_bricks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            if item.total_items:
                op = row.operator("bim.view_brick_class", text="", icon="DISCLOSURE_TRI_RIGHT", emboss=False)
                op.brick_class = item.name
            row.label(text=item.name)
            if item.total_items:
                row.label(text=str(item.total_items))

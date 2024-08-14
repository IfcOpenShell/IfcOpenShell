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

from bpy.types import Panel
from bonsai.bim.module.web.data import WebData


class BIM_PT_webui(Panel):
    bl_label = "Web UI"
    bl_idname = "BIM_PT_webui"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_collaboration"

    def draw(self, context):

        if not WebData.is_loaded:
            WebData.load()

        layout = self.layout

        scene = context.scene
        props = scene.WebProperties

        row = layout.row()
        row.prop(props, "webserver_port", text="Websocket server Port")

        if props.is_running:
            row = layout.row()
            row.label(text=f"Running on port: {props.webserver_port}")

        row = layout.row(align=True)
        row.operator("bim.connect_websocket_server")
        row.operator("bim.open_web_browser", icon="URL", text="")

        if props.is_connected:
            row = layout.row()
            row.label(text=f"Connected on port: {props.webserver_port}")

        if props.is_running:
            row = layout.row()
            row.operator("bim.kill_websocket_server")

        if props.is_connected:
            row = layout.row()
            row.operator("bim.disconnect_websocket_server")

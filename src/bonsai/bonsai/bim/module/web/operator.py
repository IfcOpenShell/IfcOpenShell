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

import os
import bpy
import bonsai.core.web as core
import bonsai.tool as tool


class ConnectToWebsocketServer(bpy.types.Operator):
    bl_idname = "bim.connect_websocket_server"
    bl_label = "Connect/Start websocket server"
    bl_description = "Start/Connect to a Websocket server"
    page: bpy.props.StringProperty(default="")

    def execute(self, context):
        port = context.scene.WebProperties.webserver_port
        if port == 0:
            context.scene.WebProperties.webserver_port = core.generate_port_number(tool.Web)

        port = context.scene.WebProperties.webserver_port
        core.connect_websocket_server(tool.Web, port, self.page)
        return {"FINISHED"}


class DisconnectWebsocketServer(bpy.types.Operator):
    bl_idname = "bim.disconnect_websocket_server"
    bl_label = "Disconnect from websocket server"
    bl_description = "disconnect from current websocket server"

    def execute(self, context):
        core.disconnect_websocket_server(tool.Web)
        return {"FINISHED"}


class killWebsocketServer(bpy.types.Operator):
    bl_idname = "bim.kill_websocket_server"
    bl_label = "Kill websocket server"
    bl_description = "Kill running websocket server"

    def execute(self, context):
        core.kill_websocket_server(tool.Web)
        return {"FINISHED"}


class OpenWebBrowser(bpy.types.Operator):
    bl_idname = "bim.open_web_browser"
    bl_label = "Open Web Browser"
    bl_description = "Open the web UI page URL in your Web Browser"
    page: bpy.props.StringProperty(default="")

    def execute(self, context):
        port = context.scene.WebProperties.webserver_port
        core.open_web_browser(tool.Web, port, self.page)
        return {"FINISHED"}

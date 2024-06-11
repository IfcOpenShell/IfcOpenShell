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

import os
import bpy
import blenderbim.core.web as core
import blenderbim.tool as tool


class ConnectToWebsocketServer(bpy.types.Operator):
    bl_idname = "bim.connect_websocket_server"
    bl_label = "Connect/Start websocket server"
    bl_description = "Start/Connect to a Websocket server"

    def execute(self, context):
        port = context.scene.WebProperties.Webserver_port
        if port == 0:
            context.scene.WebProperties.Webserver_port = core.generate_port_number(tool.Web)

        port = context.scene.WebProperties.Webserver_port
        core.connect_websocket_server(tool.Web, port)
        return {"FINISHED"}


class killWebsocketServer(bpy.types.Operator):
    bl_idname = "bim.kill_websocket_server"
    bl_label = "Kill websocket server"
    bl_description = "Kill running websocket server"

    def execute(self, context):
        return {"FINISHED"}

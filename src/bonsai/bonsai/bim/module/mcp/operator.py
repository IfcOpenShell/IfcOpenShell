# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
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

# This file was generated with the assistance of an AI coding tool.

import bpy

import bonsai.tool as tool

from . import server


class StartMcpBridge(bpy.types.Operator):
    bl_idname = "bim.start_mcp_bridge"
    bl_label = "Start MCP Bridge"
    bl_description = "Let ifcmcp --bonsai query and edit the open IFC model over a local socket"

    def execute(self, context):
        port = context.scene.BIMMcpProperties.port
        try:
            server.start(port)
        except (OSError, RuntimeError) as e:
            self.report({"ERROR"}, f"Could not start the MCP bridge on port {port}: {e}")
            return {"CANCELLED"}
        self.report({"INFO"}, f"MCP bridge listening on port {port}")
        return {"FINISHED"}


class StopMcpBridge(bpy.types.Operator):
    bl_idname = "bim.stop_mcp_bridge"
    bl_label = "Stop MCP Bridge"
    bl_description = "Stop answering ifcmcp requests"

    def execute(self, context):
        server.stop()
        return {"FINISHED"}


class McpEdit(bpy.types.Operator, tool.Ifc.Operator):
    """Make an edit sent by ifcmcp one undo step, and update objects to match it."""

    bl_idname = "bim.mcp_edit"
    bl_label = "MCP Edit"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def _execute(self, context):
        server.adopt_edit()
        return {"FINISHED"}

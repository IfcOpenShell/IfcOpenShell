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

from bpy.types import Panel

from . import server


class BIM_PT_mcp_bridge(Panel):
    bl_label = "MCP Bridge"
    bl_idname = "BIM_PT_mcp_bridge"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_collaboration"

    def draw(self, context):
        assert self.layout
        layout = self.layout
        if server.is_running():
            layout.label(text=f"Listening on port {server.port()}", icon="LINKED")
            layout.operator("bim.stop_mcp_bridge", icon="CANCEL")
        else:
            layout.prop(context.scene.BIMMcpProperties, "port")
            layout.operator("bim.start_mcp_bridge", icon="PLAY")

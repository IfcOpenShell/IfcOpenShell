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

from . import operator, prop, ui

classes = (
    operator.ConnectToWebsocketServer,
    operator.DisconnectWebsocketServer,
    operator.killWebsocketServer,
    operator.OpenWebBrowser,
    prop.WebProperties,
    ui.BIM_PT_webui,
)


def register():
    import bonsai.tool as tool

    bpy.types.Scene.WebProperties = bpy.props.PointerProperty(type=prop.WebProperties)
    # Honours the "Keep Web Connection" preference; stops at once if it is off.
    # Delayed so preferences are readable, and never runs in background mode.
    tool.Web.ensure_keep_connection_timer(first_interval=3.0)


def unregister():
    import bonsai.tool.web as web

    if web.keep_connection_timer is not None and bpy.app.timers.is_registered(web.keep_connection_timer):
        bpy.app.timers.unregister(web.keep_connection_timer)
    del bpy.types.Scene.WebProperties

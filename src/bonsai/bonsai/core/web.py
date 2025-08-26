# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def generate_port_number(web: type[tool.Web]) -> int:
    return web.generate_port_number()


def connect_websocket_server(web: type[tool.Web], port: int, page: str) -> None:
    # check if port already has a server listening to it
    if web.is_port_available(port):
        web.start_websocket_server(port)
        if web.has_started(port):
            web.connect_websocket_server(port)
            web.send_theme_data()
            web.open_web_browser(port, page)
        return

    web.connect_websocket_server(port)


def disconnect_websocket_server(web: type[tool.Web]) -> None:
    web.disconnect_websocket_server()


def kill_websocket_server(web: type[tool.Web]) -> None:
    web.kill_websocket_server()


def open_web_browser(web: type[tool.Web], port: int, page: str) -> None:
    web.open_web_browser(port, page)

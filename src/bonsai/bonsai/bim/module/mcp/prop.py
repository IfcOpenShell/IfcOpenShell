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

from typing import TYPE_CHECKING

from bpy.props import IntProperty
from bpy.types import PropertyGroup

from . import server


class BIMMcpProperties(PropertyGroup):
    port: IntProperty(
        name="Port",
        description="Local port that ifcmcp --bonsai connects to",
        default=server.DEFAULT_PORT,
        min=1,
        max=65535,
    )

    if TYPE_CHECKING:
        port: int

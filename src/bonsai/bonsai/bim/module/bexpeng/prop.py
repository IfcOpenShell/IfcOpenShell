# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bonsai contributors
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


from typing import TYPE_CHECKING

import bpy
from bpy.props import StringProperty
from bpy.types import PropertyGroup


class BIMBexpengProperties(PropertyGroup):
    """Scene-level properties for the BExpEng integration."""

    bindings_json: StringProperty(
        name="BExpEng Bindings",
        description="JSON object mapping full property data path to bound BExpEng parameter name.",
        default="{}",
    )

    if TYPE_CHECKING:
        bindings_json: str

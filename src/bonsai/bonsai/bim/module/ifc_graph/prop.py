# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

from bpy.props import StringProperty
from bpy.types import PropertyGroup


class IfcGraphAttribute(PropertyGroup):
    """A scalar IFC attribute displayed as a text row inside a graph node."""

    name: StringProperty(name="Name")
    value: StringProperty(name="Value")

    if TYPE_CHECKING:
        name: str
        value: str

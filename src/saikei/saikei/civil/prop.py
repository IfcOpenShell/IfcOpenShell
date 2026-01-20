# ==============================================================================
# Saikei Civil - Civil Engineering Tools for Blender
# Copyright (c) 2025 Michael Yoder / Desert Springs Civil Engineering PLLC
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Primary Author: Michael Yoder
# Company: Desert Springs Civil Engineering PLLC
# ==============================================================================


"""Global properties for Saikei Civil addon"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, StringProperty


class SaikeiCivilProperties(PropertyGroup):
    """Global properties for the Saikei Civil addon"""

    is_editing: BoolProperty(
        name="Is Editing",
        description="Whether an alignment is currently being edited",
        default=False,
    )

    status_message: StringProperty(
        name="Status Message",
        description="Current status message to display in UI",
        default="",
    )

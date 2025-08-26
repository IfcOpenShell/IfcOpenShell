# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

# ############################################################################ #

# Hey there! Welcome to the Bonsai code. Please feel free to reach
# out if you have any questions or need further guidance. Happy hacking!

# ############################################################################ #

# Every module has a tool file which implements all the functions that the core
# needs. Whereas the core is simply high level code, the tool file has the
# concrete implementations, dealing with exactly how things interact with
# Blender's property systems, IFC's data structures, the filesystem, geometry
# processing, and more.

from __future__ import annotations

import bpy
import ifcopenshell
import bonsai.core.tool
import bonsai.tool as tool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.demo.prop import BIMDemoProperties


# There is always one class in each tool file, which implements the interface
# defined by `core/tool.py`.
class Demo(bonsai.core.tool.Demo):
    @classmethod
    def get_demo_props(cls) -> BIMDemoProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMDemoProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def clear_name_field(cls) -> None:
        # In this concrete implementation, we see that "clear name field"
        # actually translates to "set this Blender string property to empty
        # string". In this case, it's pretty simple - but even simple scenarios
        # like these are important to implement in the tool, as it makes the
        # pseudocode easier to read in the core, and makes it easier to test
        # implementations separately from control flow. It also makes it easy to
        # refactor and share functions, where every tool function is captured by
        # a function name that describes its intention.
        props = cls.get_demo_props()
        props.name = ""

    @classmethod
    def get_project(cls) -> ifcopenshell.entity_instance:
        return tool.Ifc.get().by_type("IfcProject")[0]

    @classmethod
    def hide_user_hints(cls) -> None:
        props = cls.get_demo_props()
        props.show_hints = False

    @classmethod
    def set_message(cls, message) -> None:
        props = cls.get_demo_props()
        props.message = message

    @classmethod
    def show_user_hints(cls) -> None:
        props = cls.get_demo_props()
        props.show_hints = True

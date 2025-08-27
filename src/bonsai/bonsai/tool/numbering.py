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
import bonsai.core.tool
import bonsai.tool as tool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.numbering.prop import BIMNumberingProperties


class Numbering(bonsai.core.tool.Numbering):
    @classmethod
    def get_numbering_props(cls) -> BIMNumberingProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMNumberingProperties  # pyright: ignore[reportAttributeAccessIssue]

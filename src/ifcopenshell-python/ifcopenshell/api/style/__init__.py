# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""Manage visual styles of geometry (colours, transparency, rendering, etc)

Geometry may have visual styles associated with it, including surface styles,
2D curve styles, text styles, and more. Surface styles are most commonly used
for simple colouring.
"""

from .. import wrap_usecases
from .add_style import add_style
from .add_surface_style import add_surface_style
from .add_surface_textures import add_surface_textures
from .assign_material_style import assign_material_style
from .assign_representation_styles import assign_representation_styles
from .edit_presentation_style import edit_presentation_style
from .edit_surface_style import edit_surface_style
from .remove_style import remove_style
from .remove_styled_representation import remove_styled_representation
from .remove_surface_style import remove_surface_style
from .unassign_material_style import unassign_material_style
from .unassign_representation_styles import unassign_representation_styles

wrap_usecases(__path__, __name__)

__all__ = [
    "add_style",
    "add_surface_style",
    "add_surface_textures",
    "assign_material_style",
    "assign_representation_styles",
    "edit_presentation_style",
    "edit_surface_style",
    "remove_style",
    "remove_styled_representation",
    "remove_surface_style",
    "unassign_material_style",
    "unassign_representation_styles",
]

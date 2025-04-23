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

"""Boundaries are primarily used for representing virtual interfaces between
spaces for energy analysis.

Boundaries may be associated with spaces or physical elements that enclose
spaces such as walls, doors, and windows.
"""

from .. import wrap_usecases
from .assign_connection_geometry import assign_connection_geometry
from .copy_boundary import copy_boundary
from .edit_attributes import edit_attributes
from .remove_boundary import remove_boundary

wrap_usecases(__path__, __name__)

__all__ = [
    "assign_connection_geometry",
    "copy_boundary",
    "edit_attributes",
    "remove_boundary",
]

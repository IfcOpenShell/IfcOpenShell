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

"""Manage common construction types of physical elements

Almost all constructed elements may be grouped into "types". Types include wall
types, window types, column types, equipment types, and more.

Using types is critical to the success of any project.
"""

from .. import wrap_usecases
from .assign_type import assign_type
from .map_type_representations import map_type_representations
from .unassign_type import unassign_type

wrap_usecases(__path__, __name__)

__all__ = [
    "assign_type",
    "map_type_representations",
    "unassign_type",
]

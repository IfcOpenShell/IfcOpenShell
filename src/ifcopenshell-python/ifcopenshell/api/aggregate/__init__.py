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

"""Aggregates is the concept of breaking down larger wholes into smaller parts.

For example, spatial elements such as sites are broken down into one or more
buildings, and a building is broken down into storeys. Another example is for
physical elements, such as how a wall is made out of members and coverings.
"""

from .. import wrap_usecases
from .assign_object import assign_object
from .unassign_object import unassign_object

wrap_usecases(__path__, __name__)

__all__ = [
    "assign_object",
    "unassign_object",
]

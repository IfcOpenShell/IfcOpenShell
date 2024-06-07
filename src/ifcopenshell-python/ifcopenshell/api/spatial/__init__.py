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

"""Assign spatial relationships such as when an element is in a space

Physical elements (walls, doors, etc) may be contained in or reference spatial
elements (spaces, storeys, buildings, etc).
"""

from .. import wrap_usecases
from .assign_container import assign_container
from .dereference_structure import dereference_structure
from .reference_structure import reference_structure
from .unassign_container import unassign_container

wrap_usecases(__path__, __name__)

__all__ = [
    "assign_container",
    "dereference_structure",
    "reference_structure",
    "unassign_container",
]

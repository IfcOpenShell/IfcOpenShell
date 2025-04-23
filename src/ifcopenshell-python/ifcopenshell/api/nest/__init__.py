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

"""Nesting is when a component is attached to a host element

Examples include when a faucet is attached using a predrilled hole in a basin,
or when a modular connection occurs through a connection point. This implies
that when a host element moves, the child nested components must move as well.

Note that this API is not meant to be used for connection points on
distribution systems. For that purpose, such as for pipe fittings and
equipment, please see :mod:`ifcopenshell.api.system`.
"""

from .. import wrap_usecases
from .assign_object import assign_object
from .change_nest import change_nest
from .reorder_nesting import reorder_nesting
from .unassign_object import unassign_object

wrap_usecases(__path__, __name__)

__all__ = [
    "assign_object",
    "change_nest",
    "reorder_nesting",
    "unassign_object",
]

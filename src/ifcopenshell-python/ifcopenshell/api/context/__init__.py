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

"""Contexts allow you to classify when geometry should be used in different
purposes

For example, a door may have many geometries assigned to it: a 3D body
geometry, a clearance zone for disabled access and egress, and a 2D top down
plan view representation annotating swing extents. Each geometry is assigned to
a context to distinguish its purpose and level of detail.
"""

from .. import wrap_usecases
from .add_context import add_context
from .edit_context import edit_context
from .remove_context import remove_context

wrap_usecases(__path__, __name__)

__all__ = [
    "add_context",
    "edit_context",
    "remove_context",
]

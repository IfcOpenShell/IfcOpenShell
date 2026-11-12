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

"""Elements may be arbitrarily assigned to groups for organisation

Groups are useful for filtering elements or non-hierarchical organisation of a
model. Note that this only targets arbitrary groups. If you want to group
elements into a distribution system, see :mod:`ifcopenshell.api.system`.
"""

from .. import wrap_usecases
from .add_group import add_group
from .assign_group import assign_group
from .edit_group import edit_group
from .remove_group import remove_group
from .unassign_group import unassign_group
from .update_group_products import update_group_products

wrap_usecases(__path__, __name__)

__all__ = [
    "add_group",
    "assign_group",
    "edit_group",
    "remove_group",
    "unassign_group",
    "update_group_products",
]

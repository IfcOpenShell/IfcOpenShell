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

"""Manage construction and maintenance resources

Resources include equipment (cranes, etc), labour, material, and products. They
are typically referenced in construction planning, maintenance schedules, or
cost items.
"""

from .. import wrap_usecases
from .add_resource import add_resource
from .add_resource_quantity import add_resource_quantity
from .add_resource_time import add_resource_time
from .assign_resource import assign_resource
from .calculate_resource_usage import calculate_resource_usage
from .calculate_resource_work import calculate_resource_work
from .edit_resource import edit_resource
from .edit_resource_quantity import edit_resource_quantity
from .edit_resource_time import edit_resource_time
from .remove_resource import remove_resource
from .remove_resource_quantity import remove_resource_quantity
from .unassign_resource import unassign_resource

wrap_usecases(__path__, __name__)

__all__ = [
    "add_resource",
    "add_resource_quantity",
    "add_resource_time",
    "assign_resource",
    "calculate_resource_usage",
    "calculate_resource_work",
    "edit_resource",
    "edit_resource_quantity",
    "edit_resource_time",
    "remove_resource",
    "remove_resource_quantity",
    "unassign_resource",
]

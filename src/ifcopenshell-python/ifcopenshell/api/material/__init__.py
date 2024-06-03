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

"""Manage physical materials (concrete, steel, etc) and their association to
elements

IFC supports both simple materials and parametric materials (materials that
have layered thicknesses or cross sectional profiles).

Parametric materials will include parametric constraints on the geometry of
the element. These API functions do not cover that responsibility. See
:mod:`ifcopenshell.api.geometry`.

Note that this API only covers physical materials, not visual styles. If you
want to look at visual styles such as colours, transparency, shading, or
rendering options, see :mod:`ifcopenshell.api.style`.
"""

from .. import wrap_usecases
from .add_constituent import add_constituent
from .add_layer import add_layer
from .add_list_item import add_list_item
from .add_material import add_material
from .add_material_set import add_material_set
from .add_profile import add_profile
from .assign_material import assign_material
from .assign_profile import assign_profile
from .copy_material import copy_material
from .edit_assigned_material import edit_assigned_material
from .edit_constituent import edit_constituent
from .edit_layer import edit_layer
from .edit_layer_usage import edit_layer_usage
from .edit_material import edit_material
from .edit_profile import edit_profile
from .edit_profile_usage import edit_profile_usage
from .remove_constituent import remove_constituent
from .remove_layer import remove_layer
from .remove_list_item import remove_list_item
from .remove_material import remove_material
from .remove_material_set import remove_material_set
from .remove_profile import remove_profile
from .reorder_set_item import reorder_set_item
from .unassign_material import unassign_material

wrap_usecases(__path__, __name__)

__all__ = [
    "add_constituent",
    "add_layer",
    "add_list_item",
    "add_material",
    "add_material_set",
    "add_profile",
    "assign_material",
    "assign_profile",
    "copy_material",
    "edit_assigned_material",
    "edit_constituent",
    "edit_layer",
    "edit_layer_usage",
    "edit_material",
    "edit_profile",
    "edit_profile_usage",
    "remove_constituent",
    "remove_layer",
    "remove_list_item",
    "remove_material",
    "remove_material_set",
    "remove_profile",
    "reorder_set_item",
    "unassign_material",
]

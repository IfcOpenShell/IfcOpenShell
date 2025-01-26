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

"""Manage CAD layers

Note that in IFC, elements cannot be assigned to CAD layers. Instead, the
geometric representation of the element is associated to a layer.

If you want to associated a whole element to a "layer", consider using
:mod:`ifcopenshell.api.classification`.
"""

from .. import wrap_usecases
from .add_layer import add_layer
from .add_layer_with_style import add_layer_with_style
from .assign_layer import assign_layer
from .edit_layer import edit_layer
from .remove_layer import remove_layer
from .unassign_layer import unassign_layer

wrap_usecases(__path__, __name__)

__all__ = [
    "add_layer",
    "add_layer_with_style",
    "assign_layer",
    "edit_layer",
    "remove_layer",
    "unassign_layer",
]

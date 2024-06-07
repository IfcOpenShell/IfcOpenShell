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

"""Create, copy, or remove physical elements such as walls, doors, slabs, etc

This is one of the most used API modules and should be used any time you want
to create, remove, copy, or change a physical or spatial element. See
:func:`create_entity` to get started.

This module should also be used to create types. To then associate types with
elements, see :mod:`ifcopenshell.api.type`.
"""

from .. import wrap_usecases
from .copy_class import copy_class
from .create_entity import create_entity
from .reassign_class import reassign_class
from .remove_product import remove_product

wrap_usecases(__path__, __name__)

__all__ = [
    "copy_class",
    "create_entity",
    "reassign_class",
    "remove_product",
]

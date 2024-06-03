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

"""Property sets and quantity sets let you store simple key value metadata
associated with elements

This is the simplest and most common way to store information about an element.
For example, if a door has a fire rating, it is stored as a property.
"""

from .. import wrap_usecases
from .add_pset import add_pset
from .add_qto import add_qto
from .edit_pset import edit_pset
from .edit_qto import edit_qto
from .remove_pset import remove_pset

wrap_usecases(__path__, __name__)

__all__ = [
    "add_pset",
    "add_qto",
    "edit_pset",
    "edit_qto",
    "remove_pset",
]

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

"""Create void relationships between openings and physical elements

An opening is a special element (created using
:func:`ifcopenshell.api.root.create_entity`) that may then be used to create
voids in other elements (such as walls and slabs). These voids may then be
filled with doors, trapdoors, skylights, and so on.
"""

from .. import wrap_usecases
from .add_filling import add_filling
from .add_opening import add_opening
from .remove_filling import remove_filling
from .remove_opening import remove_opening

wrap_usecases(__path__, __name__)

__all__ = [
    "add_filling",
    "add_opening",
    "remove_filling",
    "remove_opening",
]

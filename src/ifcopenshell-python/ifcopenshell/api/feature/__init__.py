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

"""Create relationships between features (e.g. openings) and physical elements

A feature is a special element (created using
:func:`ifcopenshell.api.root.create_entity`) that may then be used to create
geometric changes in other elements (such as walls and slabs). Most commonly, a
feature would be an opening void. These voids may then be filled with doors,
trapdoors, skylights, and so on.
"""

from .. import wrap_usecases
from .add_feature import add_feature
from .add_filling import add_filling
from .remove_feature import remove_feature
from .remove_filling import remove_filling

wrap_usecases(__path__, __name__)

__all__ = [
    "add_feature",
    "add_filling",
    "remove_feature",
    "remove_filling",
]

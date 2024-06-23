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

"""Manage georeferencing metadata

IFC model geometry may have a coordinate reference system (CRS) assigned to it.
It may also optionally have a map conversion defined to transform to and from
map coordinates and project local engineering coordinates.
"""

from .. import wrap_usecases
from .add_georeferencing import add_georeferencing
from .edit_georeferencing import edit_georeferencing
from .edit_true_north import edit_true_north
from .edit_wcs import edit_wcs
from .remove_georeferencing import remove_georeferencing

wrap_usecases(__path__, __name__)

__all__ = [
    "add_georeferencing",
    "edit_georeferencing",
    "edit_true_north",
    "edit_wcs",
    "remove_georeferencing",
]

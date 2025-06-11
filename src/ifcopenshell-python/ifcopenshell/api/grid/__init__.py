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

"""Manages grid and grid axes

A grid in IFC may contain two or more axes running in two or more directions.
"""

from .. import wrap_usecases

from .create_axis_curve import create_axis_curve
from .create_grid_axis import create_grid_axis
from .remove_grid_axis import remove_grid_axis

wrap_usecases(__path__, __name__)

__all__ = [
    "create_axis_curve",
    "create_grid_axis",
    "remove_grid_axis",
]

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

"""Handles the definition of cross sectional profiles

Maintaining a clean profile library is important for structural simulations and
identification of standardised profiles for fabrication and carbon counting.
"""

from .. import wrap_usecases
from .add_arbitrary_profile import add_arbitrary_profile
from .add_arbitrary_profile_with_voids import add_arbitrary_profile_with_voids
from .add_parameterized_profile import add_parameterized_profile
from .copy_profile import copy_profile
from .edit_profile import edit_profile
from .remove_profile import remove_profile

wrap_usecases(__path__, __name__)

__all__ = [
    "add_arbitrary_profile",
    "add_arbitrary_profile_with_voids",
    "add_parameterized_profile",
    "copy_profile",
    "edit_profile",
    "remove_profile",
]

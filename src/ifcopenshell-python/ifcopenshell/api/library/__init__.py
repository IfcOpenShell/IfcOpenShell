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

"""Manage references to external libraries

An external library is any system which uses a key to store information. This
allows you to associate IFC entities with any arbitrary external database, API,
system, and so on. This is typically useful in smart building systems.
"""

from .. import wrap_usecases
from .add_library import add_library
from .add_reference import add_reference
from .assign_reference import assign_reference
from .edit_library import edit_library
from .edit_reference import edit_reference
from .remove_library import remove_library
from .remove_reference import remove_reference
from .unassign_reference import unassign_reference

wrap_usecases(__path__, __name__)

__all__ = [
    "add_library",
    "add_reference",
    "assign_reference",
    "edit_library",
    "edit_reference",
    "remove_library",
    "remove_reference",
    "unassign_reference",
]

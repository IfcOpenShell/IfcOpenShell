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

"""Define units (length, area, monetary, pressure, etc)

Units can be defined as a default project unit or used specifically for certain
properties. Units may be especially complex when dealing with services and
equipment.
"""

from .. import wrap_usecases
from .add_context_dependent_unit import add_context_dependent_unit
from .add_conversion_based_unit import add_conversion_based_unit
from .add_monetary_unit import add_monetary_unit
from .add_si_unit import add_si_unit
from .add_derived_unit import add_derived_unit
from .assign_unit import assign_unit
from .edit_derived_unit import edit_derived_unit
from .edit_monetary_unit import edit_monetary_unit
from .edit_named_unit import edit_named_unit
from .remove_unit import remove_unit
from .unassign_unit import unassign_unit

wrap_usecases(__path__, __name__)

__all__ = [
    "add_context_dependent_unit",
    "add_conversion_based_unit",
    "add_derived_unit",
    "add_monetary_unit",
    "add_si_unit",
    "assign_unit",
    "edit_derived_unit",
    "edit_monetary_unit",
    "edit_named_unit",
    "remove_unit",
    "unassign_unit",
]

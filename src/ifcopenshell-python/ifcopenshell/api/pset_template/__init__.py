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

"""Manage property templates to standard project property names and data types

To help standardise the naming, data types, and association of properties to
elements, IFC supports property set templates. buildingSMART provides their own
built-in ISO-standardised property templates, but governments, companies, and
individuals may also create their own.
"""

from .. import wrap_usecases
from .add_prop_template import add_prop_template
from .add_pset_template import add_pset_template
from .edit_prop_template import edit_prop_template
from .edit_pset_template import edit_pset_template
from .remove_prop_template import remove_prop_template
from .remove_pset_template import remove_pset_template

wrap_usecases(__path__, __name__)

__all__ = [
    "add_prop_template",
    "add_pset_template",
    "edit_prop_template",
    "edit_pset_template",
    "remove_prop_template",
    "remove_pset_template",
]

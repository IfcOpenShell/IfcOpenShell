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

"""Classification systems are a way of categorising objects

Although IFC itself comes with a built-in classification hierarchy (e.g.
IfcWall and its predefined types of PARTITIONING, etc), there are many external
or custom classification systems such as Uniclass, Omniclass and more. IFC is
able to integrate with any external classification system.

This API allows you to manage and assign external classification systems and
references.
"""

from .. import wrap_usecases
from .add_classification import add_classification
from .add_reference import add_reference
from .edit_classification import edit_classification
from .edit_reference import edit_reference
from .remove_classification import remove_classification
from .remove_reference import remove_reference

wrap_usecases(__path__, __name__)

__all__ = [
    "add_classification",
    "add_reference",
    "edit_classification",
    "edit_reference",
    "remove_classification",
    "remove_reference",
]

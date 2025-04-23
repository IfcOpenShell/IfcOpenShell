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

"""Create relationships necessary for smart annotations for drawings

Drawings may be generated from modeled elements and annotations. These
annotations may have relationships which indicate smart data being populated.
"""

from .. import wrap_usecases
from .assign_product import assign_product
from .edit_text_literal import edit_text_literal
from .unassign_product import unassign_product

wrap_usecases(__path__, __name__)

__all__ = [
    "assign_product",
    "edit_text_literal",
    "unassign_product",
]

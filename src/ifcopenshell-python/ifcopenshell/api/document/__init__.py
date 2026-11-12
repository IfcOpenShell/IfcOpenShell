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

"""Reference external project documents and associate them to model elements

Some project information (drawings, specifications, certificates, reports, etc)
may be stored in external documents (locally or in a CDE). IFC lets you store a
register of documents with metadata and associate them with elements (both
physical and non-physical).
"""

from .. import wrap_usecases
from .add_information import add_information
from .add_reference import add_reference
from .assign_document import assign_document
from .edit_information import edit_information
from .edit_reference import edit_reference
from .remove_information import remove_information
from .remove_reference import remove_reference
from .unassign_document import unassign_document

wrap_usecases(__path__, __name__)

__all__ = [
    "add_information",
    "add_reference",
    "assign_document",
    "edit_information",
    "edit_reference",
    "remove_information",
    "remove_reference",
    "unassign_document",
]

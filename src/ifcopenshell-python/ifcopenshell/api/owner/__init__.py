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

"""An element may have an owner, indicating who is responsible, liable, or
contactable regarding that element

Note that in IFC2X3, element ownership is mandatory and must be addressed prior
to the creation of any element at all. See :func:`create_owner_history` for
examples.
"""

from .. import wrap_usecases
from .add_actor import add_actor
from .add_address import add_address
from .add_application import add_application
from .add_organisation import add_organisation
from .add_person import add_person
from .add_person_and_organisation import add_person_and_organisation
from .add_role import add_role
from .assign_actor import assign_actor
from .create_owner_history import create_owner_history
from .edit_actor import edit_actor
from .edit_address import edit_address
from .edit_application import edit_application
from .edit_organisation import edit_organisation
from .edit_person import edit_person
from .edit_role import edit_role
from .remove_actor import remove_actor
from .remove_address import remove_address
from .remove_application import remove_application
from .remove_organisation import remove_organisation
from .remove_person import remove_person
from .remove_person_and_organisation import remove_person_and_organisation
from .remove_role import remove_role
from .unassign_actor import unassign_actor
from .update_owner_history import update_owner_history

wrap_usecases(__path__, __name__)

__all__ = [
    "add_actor",
    "add_address",
    "add_application",
    "add_organisation",
    "add_person",
    "add_person_and_organisation",
    "add_role",
    "assign_actor",
    "create_owner_history",
    "edit_actor",
    "edit_address",
    "edit_application",
    "edit_organisation",
    "edit_person",
    "edit_role",
    "remove_actor",
    "remove_address",
    "remove_application",
    "remove_organisation",
    "remove_person",
    "remove_person_and_organisation",
    "remove_role",
    "unassign_actor",
    "update_owner_history",
]

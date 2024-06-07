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

"""Manage distribution systems and port connectivity

Service distribution systems (mechanical, electrical, hydraulic, fire,
logistical, etc) consist of connected distribution segments, fittings,
terminals, control equipment, and more. This module handles port connectivity
and relationships describing distribution flow.
"""

from .. import wrap_usecases
from .add_port import add_port
from .add_system import add_system
from .assign_flow_control import assign_flow_control
from .assign_port import assign_port
from .assign_system import assign_system
from .connect_port import connect_port
from .disconnect_port import disconnect_port
from .edit_system import edit_system
from .remove_system import remove_system
from .unassign_flow_control import unassign_flow_control
from .unassign_port import unassign_port
from .unassign_system import unassign_system

wrap_usecases(__path__, __name__)

__all__ = [
    "add_port",
    "add_system",
    "assign_flow_control",
    "assign_port",
    "assign_system",
    "connect_port",
    "disconnect_port",
    "edit_system",
    "remove_system",
    "unassign_flow_control",
    "unassign_port",
    "unassign_system",
]

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

"""Manage analytical properties for structural simulation

This only handles authoring the analytical model, and does not actually perform
any structural simulation. To perform the simulation, see IFC2CA.
"""

from .. import wrap_usecases
from .add_structural_activity import add_structural_activity
from .add_structural_analysis_model import add_structural_analysis_model
from .add_structural_boundary_condition import add_structural_boundary_condition
from .add_structural_load import add_structural_load
from .add_structural_load_case import add_structural_load_case
from .add_structural_load_group import add_structural_load_group
from .add_structural_member_connection import add_structural_member_connection
from .assign_structural_analysis_model import assign_structural_analysis_model
from .edit_structural_analysis_model import edit_structural_analysis_model
from .edit_structural_boundary_condition import edit_structural_boundary_condition
from .edit_structural_connection_cs import edit_structural_connection_cs
from .edit_structural_item_axis import edit_structural_item_axis
from .edit_structural_load import edit_structural_load
from .edit_structural_load_case import edit_structural_load_case
from .remove_structural_analysis_model import remove_structural_analysis_model
from .remove_structural_boundary_condition import remove_structural_boundary_condition
from .remove_structural_connection_condition import remove_structural_connection_condition
from .remove_structural_load import remove_structural_load
from .remove_structural_load_case import remove_structural_load_case
from .remove_structural_load_group import remove_structural_load_group
from .unassign_structural_analysis_model import unassign_structural_analysis_model

wrap_usecases(__path__, __name__)

__all__ = [
    "add_structural_activity",
    "add_structural_analysis_model",
    "add_structural_boundary_condition",
    "add_structural_load",
    "add_structural_load_case",
    "add_structural_load_group",
    "add_structural_member_connection",
    "assign_structural_analysis_model",
    "edit_structural_analysis_model",
    "edit_structural_boundary_condition",
    "edit_structural_connection_cs",
    "edit_structural_item_axis",
    "edit_structural_load",
    "edit_structural_load_case",
    "remove_structural_analysis_model",
    "remove_structural_boundary_condition",
    "remove_structural_connection_condition",
    "remove_structural_load",
    "remove_structural_load_case",
    "remove_structural_load_group",
    "unassign_structural_analysis_model",
]

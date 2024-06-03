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

"""Constraints are an advanced feature allowing you to specify parametric
limits on properties

Warning: usage of constraints are mostly untested in real life applications.
"""

from .. import wrap_usecases
from .add_metric import add_metric
from .add_metric_reference import add_metric_reference
from .add_objective import add_objective
from .assign_constraint import assign_constraint
from .edit_metric import edit_metric
from .edit_objective import edit_objective
from .remove_constraint import remove_constraint
from .remove_metric import remove_metric
from .unassign_constraint import unassign_constraint

wrap_usecases(__path__, __name__)

__all__ = [
    "add_metric",
    "add_metric_reference",
    "add_objective",
    "assign_constraint",
    "edit_metric",
    "edit_objective",
    "remove_constraint",
    "remove_metric",
    "unassign_constraint",
]

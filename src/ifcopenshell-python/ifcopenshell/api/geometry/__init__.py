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

"""Create geometric representations and assign them to elements

These functions support both the creation of arbitrary geometry as well as
geometry that follows parametric rules (e.g. layered geometry or profiled
geometry extrusions).
"""

from .. import wrap_usecases
from .add_axis_representation import add_axis_representation
from .add_boolean import add_boolean

try:
    from .add_door_representation import add_door_representation
except ModuleNotFoundError as e:
    print(f"Note: API not available due to missing dependencies: geometry.add_door_representation - {e}")
from .add_footprint_representation import add_footprint_representation
from .add_mesh_representation import add_mesh_representation
from .add_profile_representation import add_profile_representation

try:
    from .add_railing_representation import add_railing_representation
except ModuleNotFoundError as e:
    print(f"Note: API not available due to missing dependencies: geometry.add_railing_representation - {e}")

try:
    from .add_representation import add_representation
except ModuleNotFoundError as e:
    print(f"Note: API not available due to missing dependencies: geometry.add_representation - {e}")
from .add_slab_representation import add_slab_representation
from .add_wall_representation import add_wall_representation

try:
    from .add_window_representation import add_window_representation
except ModuleNotFoundError as e:
    print(f"Note: API not available due to missing dependencies: geometry.add_window_representation - {e}")
from .assign_representation import assign_representation
from .connect_element import connect_element
from .connect_path import connect_path
from .create_2pt_wall import create_2pt_wall
from .disconnect_element import disconnect_element
from .disconnect_path import disconnect_path
from .edit_object_placement import edit_object_placement
from .map_representation import map_representation
from .remove_boolean import remove_boolean
from .remove_representation import remove_representation
from .unassign_representation import unassign_representation

wrap_usecases(__path__, __name__)

__all__ = [
    "add_axis_representation",
    "add_boolean",
    "add_door_representation",
    "add_footprint_representation",
    "add_mesh_representation",
    "add_profile_representation",
    "add_railing_representation",
    "add_representation",
    "add_slab_representation",
    "add_wall_representation",
    "add_window_representation",
    "assign_representation",
    "connect_element",
    "connect_path",
    "create_2pt_wall",
    "disconnect_element",
    "disconnect_path",
    "edit_object_placement",
    "map_representation",
    "remove_boolean",
    "remove_representation",
    "unassign_representation",
]

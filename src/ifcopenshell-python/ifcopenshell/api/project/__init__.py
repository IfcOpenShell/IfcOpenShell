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

"""Create an IFC project

All IFCs must have one, and only one IFC project before any data may be
associated. If you are starting from scratch, see :func:create_file.

Once a project exists, you may optionally create project libraries and
associate type assets with it. You may also append assets from other projects
into your project.
"""

from .. import wrap_usecases
from .append_asset import append_asset
from .assign_declaration import assign_declaration
from .create_file import create_file
from .unassign_declaration import unassign_declaration

wrap_usecases(__path__, __name__)

__all__ = [
    "append_asset",
    "assign_declaration",
    "create_file",
    "unassign_declaration",
]

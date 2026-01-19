# Saikei Civil - Civil Engineering Tools for IfcOpenShell
# Copyright (C) 2025 IfcOpenShell Contributors
#
# This file is part of Saikei Civil.
#
# Saikei Civil is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Saikei Civil is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Saikei Civil.  If not, see <http://www.gnu.org/licenses/>.

"""Saikei Civil Tool Module

This module contains Blender-specific implementations that bridge the
core business logic to the Blender environment.

Following Bonsai's architecture pattern:
- core/ = Pure Python logic
- tool/ = Blender implementations with bpy (this module)
- civil/ = UI layer (operators, panels, properties)

Usage:
    from .... import tool  # relative import from within saikei package
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Ifc.get()
"""

from .alignment import Alignment

# Re-export Bonsai's tools that we use directly
try:
    from bonsai.tool import Ifc, Collector
except ImportError:
    # Fallback for when Bonsai is not available
    Ifc = None
    Collector = None

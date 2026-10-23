# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

"""Shared module-level state for the light/radiance pipeline.

These globals are populated by ExportOBJ, consumed by PrepareRadianceScene,
and read by RadianceRender. They must live in a shared module so that
all operator files can access the same state.
"""

# Collected IFC material names from the most recent export
ifc_materials: list[str] = []

# The prepared pyradiance Scene object (set by PrepareRadianceScene, read by RadianceRender)
scene = None

# Info about exported linked models: list of (obj_path, mtl_path, link_matrix_4x4)
linked_model_exports: list[tuple[str, str, list[list[float]]]] = []

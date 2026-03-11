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

"""Thin re-export module for backward compatibility.

All operator classes are defined in their respective submodules:
  - export.py:   ExportOBJ, CleanupRadianceFiles
  - prepare.py:  PrepareRadianceScene
  - render.py:   RadianceRender, FalseColorRadiance
  - solar.py:    ImportTrueNorth, ImportLatLong, MoveSunPathTo3DCursor,
                 ViewFromSun, LightPickCoordinates, LightSetTimeToNow
  - material.py: RefreshIFCMaterials, UnmapMaterial,
                 RADIANCE_OT_export_material_mappings,
                 RADIANCE_OT_import_material_mappings,
                 RADIANCE_OT_open_spectraldb
  - ies.py:      AddIESLight, RemoveIESLight

EnumPropertySearch and SetEnumProperty are provided by the global
bonsai.bim.operator module (bl_idname "bim.enum_property_search").
"""

from bonsai.bim.module.light.export import CleanupRadianceFiles, ExportOBJ  # noqa: F401
from bonsai.bim.module.light.ies import AddIESLight, RemoveIESLight  # noqa: F401
from bonsai.bim.module.light.material import (  # noqa: F401
    RADIANCE_OT_export_material_mappings,
    RADIANCE_OT_import_material_mappings,
    RADIANCE_OT_open_spectraldb,
    RefreshIFCMaterials,
    UnmapMaterial,
)
from bonsai.bim.module.light.prepare import PrepareRadianceScene  # noqa: F401
from bonsai.bim.module.light.render import (  # noqa: F401
    FalseColorRadiance,
    RadianceRender,
)
from bonsai.bim.module.light.solar import (  # noqa: F401
    ImportLatLong,
    ImportTrueNorth,
    LightPickCoordinates,
    LightSetTimeToNow,
    MoveSunPathTo3DCursor,
    ViewFromSun,
)

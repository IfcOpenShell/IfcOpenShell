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

import importlib.util
import logging
import os
import stat
from pathlib import Path

import bpy
import pyradiance

from . import list, operator, prop, ui

logger = logging.getLogger(__name__)


def get_pyradiance_path():
    return importlib.util.find_spec("pyradiance").submodule_search_locations[0]


classes = (
    operator.ExportOBJ,
    operator.ImportLatLong,
    operator.ImportTrueNorth,
    operator.MoveSunPathTo3DCursor,
    operator.RadianceRender,
    operator.ViewFromSun,
    operator.LightPickCoordinates,
    operator.LightSetTimeToNow,
    operator.RefreshIFCMaterials,
    operator.UnmapMaterial,
    operator.RADIANCE_OT_select_camera,
    operator.RADIANCE_OT_export_material_mappings,
    operator.RADIANCE_OT_import_material_mappings,
    operator.RADIANCE_OT_open_spectraldb,
    prop.RadianceMaterial,
    prop.BIMSolarProperties,
    prop.RadianceExporterProperties,
    ui.BIM_PT_radiance_exporter,
    ui.BIM_PT_solar,
    list.MATERIAL_UL_radiance_materials,
)


def register():
    bpy.types.Scene.BIMRadianceExporeterProperies = bpy.props.PointerProperty(type=prop.RadianceExporterProperties)
    bpy.types.Scene.BIMSolarProperties = bpy.props.PointerProperty(type=prop.BIMSolarProperties)

    if pyradiance:
        pyradiance_path = Path(get_pyradiance_path())
        bin_path = pyradiance_path / "bin"
        if bin_path.exists():
            for file in bin_path.iterdir():
                if not file.is_file() or os.access(file, os.X_OK):
                    # Already executable (eg. a read-only systemwide/AUR install
                    # that ships pyradiance's binaries with exec bits already set).
                    # Skip the chmod entirely so we never touch a read-only filesystem.
                    continue
                try:
                    file.chmod(file.stat().st_mode | stat.S_IEXEC)
                except PermissionError:
                    # Best effort only: some installs (eg. systemwide/AUR packages)
                    # are not writable by the running user. Registration must not
                    # fail because of it. See #7156.
                    logger.warning(f"Failed to set exec permission on '{file}'. Radiance rendering may not work.")


def unregister():
    del bpy.types.Scene.BIMRadianceExporeterProperies
    del bpy.types.Scene.BIMSolarProperties

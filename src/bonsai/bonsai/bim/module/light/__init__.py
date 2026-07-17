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


def ensure_pyradiance_binaries_executable() -> None:
    """Restore the exec bit on the pyradiance binaries we bundle.

    pyradiance's wheels already ship their ``bin/`` binaries with the exec bit
    set, but Blender installs bundled wheels with a plain ``zipfile`` extraction
    (see Blender's ``_bpy_internal/extensions/wheel_manager.py``) that discards
    unix permissions, so the binaries arrive non-executable and radiance
    rendering fails. This mirrors what ``tool.Blender.ensure_bin_in_path`` already
    does for the bundled ifcmerge binary.

    We only ever touch a pyradiance we own. Anything already executable is left
    untouched, which covers a distro/AUR package installed system-wide: the
    packager is responsible for its permissions, it is already correct, and it
    typically lives on a read-only filesystem. Any failure is best effort only and
    must never break registration. See #7156.
    """
    if not pyradiance:
        return
    bin_path = Path(get_pyradiance_path()) / "bin"
    if not bin_path.exists():
        return
    for file in bin_path.iterdir():
        if not file.is_file() or os.access(file, os.X_OK):
            continue
        try:
            file.chmod(file.stat().st_mode | stat.S_IEXEC)
        except OSError as e:
            # eg. a read-only or otherwise unwritable third-party install.
            logger.warning(f"Could not set exec permission on '{file}': {e}. Radiance rendering may not work.")


def register():
    bpy.types.Scene.BIMRadianceExporeterProperies = bpy.props.PointerProperty(type=prop.RadianceExporterProperties)
    bpy.types.Scene.BIMSolarProperties = bpy.props.PointerProperty(type=prop.BIMSolarProperties)

    ensure_pyradiance_binaries_executable()


def unregister():
    del bpy.types.Scene.BIMRadianceExporeterProperies
    del bpy.types.Scene.BIMSolarProperties

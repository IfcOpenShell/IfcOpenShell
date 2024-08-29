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

import bpy
from . import ui, prop, operator, list

import stat
from pathlib import Path

import importlib
import pyradiance


def get_pyradiance_path():
    return importlib.util.find_spec("pyradiance").submodule_search_locations[0]


classes = (
    operator.ExportOBJ,
    operator.ImportLatLong,
    operator.ImportTrueNorth,
    operator.MoveSunPathTo3DCursor,
    operator.RadianceRender,
    operator.ViewFromSun,
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
    bpy.types.Scene.radiance_exporter_properties = bpy.props.PointerProperty(type=prop.RadianceExporterProperties)
    bpy.types.Scene.BIMSolarProperties = bpy.props.PointerProperty(type=prop.BIMSolarProperties)
    pyradiance_path = Path(get_pyradiance_path())
    bin_path = pyradiance_path / "bin"
    if bin_path.exists():
        for file in bin_path.iterdir():
            if file.is_file():
                file.chmod(file.stat().st_mode | stat.S_IEXEC)


def unregister():
    del bpy.types.Scene.radiance_exporter_properties
    del bpy.types.Scene.BIMSolarProperties

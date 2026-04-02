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
import stat
from pathlib import Path

import bpy
import pyradiance

from . import export, ies, list, material, operator, prepare, prop, render, solar, ui


def get_pyradiance_path():
    return importlib.util.find_spec("pyradiance").submodule_search_locations[0]


classes = (
    export.ExportOBJ,
    solar.ImportLatLong,
    solar.ImportTrueNorth,
    solar.MoveSunPathTo3DCursor,
    render.RadianceRender,
    render.FalseColorRadiance,
    solar.ViewFromSun,
    solar.LightPickCoordinates,
    solar.LightSetTimeToNow,
    material.RefreshIFCMaterials,
    material.UnmapMaterial,
    material.RADIANCE_OT_export_material_mappings,
    material.RADIANCE_OT_import_material_mappings,
    material.RADIANCE_OT_open_spectraldb,
    operator.EnumPropertySearch,
    prepare.PrepareRadianceScene,
    operator.SetEnumProperty,
    ies.AddIESLight,
    ies.RemoveIESLight,
    export.CleanupRadianceFiles,
    prop.RadianceMaterial,
    prop.IESLight,
    prop.BIMSolarProperties,
    prop.RadianceExporterProperties,
    ui.BIM_PT_radiance_exporter,
    ui.BIM_PT_radiance_scene_setup,
    ui.BIM_PT_radiance_materials,
    ui.BIM_PT_radiance_lighting,
    ui.BIM_PT_radiance_render_settings,
    ui.BIM_PT_radiance_pipeline,
    ui.BIM_PT_solar,
    list.MATERIAL_UL_radiance_materials,
    list.MATERIAL_UL_ies_lights,
)


def register():
    bpy.types.Scene.BIMRadianceExporterProperties = bpy.props.PointerProperty(type=prop.RadianceExporterProperties)
    bpy.types.Scene.BIMSolarProperties = bpy.props.PointerProperty(type=prop.BIMSolarProperties)

    if pyradiance:
        pyradiance_path = Path(get_pyradiance_path())
        bin_path = pyradiance_path / "bin"
        if bin_path.exists():
            for file in bin_path.iterdir():
                if file.is_file():
                    file.chmod(file.stat().st_mode | stat.S_IEXEC)


def unregister():
    del bpy.types.Scene.BIMRadianceExporterProperties
    del bpy.types.Scene.BIMSolarProperties

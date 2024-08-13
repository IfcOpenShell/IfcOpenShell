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

import bpy.props
import bpy.types


class CoveToolProject(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    run_set: bpy.props.StringProperty(name="Run Set")
    url: bpy.props.StringProperty(name="URL")


class CoveToolSimpleAnalysis(bpy.types.PropertyGroup):
    si_units: bpy.props.BoolProperty(name="SI Units")
    building_height: bpy.props.StringProperty(name="Building Height")
    roof_area: bpy.props.StringProperty(name="Roof Area")
    floor_area: bpy.props.StringProperty(name="Floor Area")
    skylight_area: bpy.props.StringProperty(name="Skylight Area")
    wall_area_e: bpy.props.StringProperty(name="Wall Area E")
    wall_area_ne: bpy.props.StringProperty(name="Wall Area NE")
    wall_area_n: bpy.props.StringProperty(name="Wall Area N")
    wall_area_nw: bpy.props.StringProperty(name="Wall Area NW")
    wall_area_w: bpy.props.StringProperty(name="Wall Area W")
    wall_area_sw: bpy.props.StringProperty(name="Wall Area SW")
    wall_area_s: bpy.props.StringProperty(name="Wall Area S")
    wall_area_se: bpy.props.StringProperty(name="Wall Area SE")
    window_area_e: bpy.props.StringProperty(name="Window Area E")
    window_area_ne: bpy.props.StringProperty(name="Window Area NE")
    window_area_n: bpy.props.StringProperty(name="Window Area N")
    window_area_nw: bpy.props.StringProperty(name="Window Area NW")
    window_area_w: bpy.props.StringProperty(name="Window Area W")
    window_area_sw: bpy.props.StringProperty(name="Window Area SW")
    window_area_s: bpy.props.StringProperty(name="Window Area S")
    window_area_se: bpy.props.StringProperty(name="Window Area SE")


class CoveToolProperties(bpy.types.PropertyGroup):
    username: bpy.props.StringProperty(name="Username")
    password: bpy.props.StringProperty(name="Password")
    token: bpy.props.StringProperty(name="Token")
    projects: bpy.props.CollectionProperty(name="Projects", type=CoveToolProject)
    active_project_index: bpy.props.IntProperty(name="Active Project Index")
    simple_analysis: bpy.props.PointerProperty(type=CoveToolSimpleAnalysis)

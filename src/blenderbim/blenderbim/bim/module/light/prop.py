# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import pytz
import tzfpy
import datetime
import blenderbim.tool as tool
from math import radians, pi
from mathutils import Euler, Vector, Matrix, Quaternion
from bpy.props import IntProperty, StringProperty, EnumProperty, FloatProperty, FloatVectorProperty, BoolProperty
from bpy.types import PropertyGroup
from blenderbim.bim.module.light.data import SolarData
from blenderbim.bim.module.light.decorator import SolarDecorator

sun_position = tool.Blender.get_sun_position_addon()


def get_sites(self, context):
    if not SolarData.is_loaded:
        SolarData.load()
    return SolarData.data["sites"]


def update_latlong(self, context):
    sun_props = context.scene.sun_pos_properties
    sun_props.latitude = self.latitude
    sun_props.longitude = self.longitude
    update_sun_path()


def update_hourminute(self, context):
    sun_props = context.scene.sun_pos_properties
    sun_props.time = self.hour + (self.minute / 60)
    update_sun_path()


def update_date(self, context):
    sun_props = context.scene.sun_pos_properties
    sun_props.month = self.month
    sun_props.day = self.day
    update_sun_path()


def update_true_north(self, context):
    sun_props = context.scene.sun_pos_properties
    # Preserve IFC sign convention
    sun_props.north_offset = radians(self.true_north * -1)
    update_sun_path()


def update_sun_path_size(self, context):
    sun_props = context.scene.sun_pos_properties
    sun_props.sun_distance = self.sun_path_size
    update_sun_path()


def update_display_shadows(self, context):
    if self.display_shadows:
        update_sun_path()
        context.scene.render.engine = "BLENDER_WORKBENCH"
        context.scene.display.shading.light = "FLAT"
        context.scene.display.shading.show_shadows = True
        context.scene.display.shading.show_object_outline = True
        context.scene.display.shadow_focus = 1.0
        context.scene.view_settings.view_transform = "Standard"  # Preserve shading colours
        space = tool.Blender.get_view3d_space()
        space.shading.type = "RENDERED"
    else:
        space = tool.Blender.get_view3d_space()
        space.shading.type = "SOLID"


def update_display_sun_path(self, context):
    if self.display_sun_path:
        update_sun_path()
        SolarDecorator.install(bpy.context)
    else:
        SolarDecorator.uninstall()


def update_sun_path():
    props = bpy.context.scene.BIMSolarProperties
    sun_props = bpy.context.scene.sun_pos_properties
    props.timezone = tzfpy.get_tz(props.longitude, props.latitude)
    timezone = pytz.timezone(props.timezone)
    dt = datetime.datetime(sun_props.year, sun_props.month, sun_props.day, props.hour, props.minute)
    local_time = timezone.localize(dt, is_dst=None)
    sun_props.use_daylight_savings = bool(local_time.dst())
    sun_props.UTC_zone = local_time.utcoffset().total_seconds() / 3600
    zone = -sun_props.UTC_zone
    if sun_props.use_daylight_savings:
        zone -= 1
    azimuth, elevation = sun_position.sun_calc.get_sun_coordinates(
        sun_props.time,
        sun_props.latitude,
        sun_props.longitude,
        zone,
        sun_props.month,
        sun_props.day,
        sun_props.year,
    )
    sun_vector = sun_position.sun_calc.get_sun_vector(azimuth, elevation) * sun_props.sun_distance
    props.sun_position = sun_vector
    # sun_vector.z = max(0, sun_vector.z)
    # Light direction is a bit weird?
    mat = Matrix(((-1.0, 0.0, 0.0, 0.0), (0.0, 0, 1.0, 0.0), (-0.0, -1.0, 0, 0.0), (0.0, 0.0, 0.0, 1.0))).inverted()
    rotation_euler = Euler((elevation - pi / 2, 0, -azimuth))
    rotation_quaternion = rotation_euler.to_quaternion()

    if sun_vector.z < 0:
        bpy.context.scene.display.light_direction = mat @ Vector((0, 0, 1))
    else:
        bpy.context.scene.display.light_direction = mat @ (rotation_quaternion @ Vector((0, 0, -1)))
    SolarData.data["sun"] = sun_vector

    if obj := bpy.data.objects.get("SunPathCamera"):
        obj.matrix_world.translation = sun_vector
        z180_quaternion = Quaternion((0, 0, 1), radians(180))
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = rotation_quaternion @ z180_quaternion
        obj.data.ortho_scale = props.sun_path_size * 2


class RadianceExporterProperties(PropertyGroup):

    def update_json_file_path(self, context):
        if self.json_file_path:
            self.json_file_path = bpy.path.abspath(self.json_file_path)

    radiance_resolution_x: IntProperty(
        name="X", description="Horizontal resolution of the output image", default=1920, min=1
    )
    radiance_resolution_y: IntProperty(
        name="Y", description="Vertical resolution of the output image", default=1080, min=1
    )
    ifc_file_name: StringProperty(
        name="IFC File Name", description="Name of the IFC file to use (without .ifc extension)", default=""
    )

    json_file_path: StringProperty(
        name="JSON File",
        description="Path to the JSON file",
        default="",
        subtype="FILE_PATH",
        update=lambda self, context: self.update_json_file_path(context),
    )

    radiance_quality: EnumProperty(
        name="Quality",
        description="Radiance rendering quality",
        items=[("LOW", "Low", "Low quality"), ("MEDIUM", "Medium", "Medium quality"), ("HIGH", "High", "High quality")],
        default="MEDIUM",
    )
    radiance_detail: EnumProperty(
        name="Detail",
        description="Radiance rendering detail",
        items=[("LOW", "Low", "Low detail"), ("MEDIUM", "Medium", "Medium detail"), ("HIGH", "High", "High detail")],
        default="MEDIUM",
    )
    radiance_variability: EnumProperty(
        name="Variability",
        description="Radiance rendering variability",
        items=[
            ("LOW", "Low", "Low variability"),
            ("MEDIUM", "Medium", "Medium variability"),
            ("HIGH", "High", "High variability"),
        ],
        default="MEDIUM",
    )


class BIMSolarProperties(PropertyGroup):
    sites: EnumProperty(items=get_sites, name="Sites")
    latitude: FloatProperty(name="Latitude", min=-90, max=90, update=update_latlong)
    longitude: FloatProperty(name="Longitude", min=-180, max=180, update=update_latlong)
    timezone: StringProperty(name="Timezone", default="Etc/GMT")
    true_north: FloatProperty(name="True North", min=-180, max=180, update=update_true_north)
    month: IntProperty(name="Month", min=1, max=12, default=1, update=update_date)
    day: IntProperty(name="Date", min=1, max=31, default=1, update=update_date)
    hour: IntProperty(name="Hour", min=0, max=23, default=12, update=update_hourminute)
    minute: IntProperty(name="Minute", min=0, max=59, update=update_hourminute)
    sun_position: FloatVectorProperty(name="Sun Position", subtype="XYZ", default=(0, 0, 0))
    sun_path_origin: FloatVectorProperty(name="Sun Path Origin", subtype="XYZ", default=(0, 0, 0))
    sun_path_size: FloatProperty(name="Sun Path Size", min=0.1, default=50, update=update_sun_path_size)
    display_shadows: BoolProperty(
        name="Display Shadows",
        default=False,
        description="Enables a visual style to display shadows easily",
        update=update_display_shadows,
    )
    display_sun_path: BoolProperty(
        name="Display Sun Path",
        default=False,
        description="Displays analemmas and sun position",
        update=update_display_sun_path,
    )

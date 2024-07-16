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
from math import radians
from bpy.props import IntProperty, StringProperty, EnumProperty, FloatProperty
from bpy.types import PropertyGroup
from blenderbim.bim.module.light.data import SolarData


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
    update_sun_path()


def update_true_north(self, context):
    sun_props = context.scene.sun_pos_properties
    # Preserve IFC sign convention
    sun_props.north_offset = radians(self.true_north * -1)


def update_sun_path():
    props = bpy.context.scene.BIMSolarProperties
    sun_props = bpy.context.scene.sun_pos_properties
    timezone = pytz.timezone(tzfpy.get_tz(props.longitude, props.latitude))
    dt = datetime.datetime(datetime.datetime.now(datetime.UTC).year, int(props.month), props.date, props.hour, props.minute)
    local_time = timezone.localize(dt, is_dst=None)
    sun_props.use_daylight_savings = bool(local_time.dst())
    sun_props.UTC_zone = local_time.utcoffset().total_seconds() / 3600


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
    true_north: FloatProperty(name="True North", min=-180, max=180, update=update_true_north)
    month: EnumProperty(
        name="Month",
        items=[
            (str(i + 1), m, "")
            for i, m in enumerate(
                (
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                )
            )
        ],
        update=update_date
    )
    date: IntProperty(name="Date", min=1, max=31, default=1, update=update_date)
    hour: IntProperty(name="Hour", min=0, max=23, update=update_hourminute)
    minute: IntProperty(name="Minute", min=0, max=59, update=update_hourminute)

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
import pytz
import tzfpy
import json
import datetime
import bonsai.tool as tool
from math import radians, pi
from mathutils import Euler, Vector, Matrix, Quaternion
from bpy.props import (
    IntProperty,
    StringProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    BoolProperty,
    CollectionProperty,
    PointerProperty,
)
import os
from bpy.types import PropertyGroup
from bonsai.bim.module.light.data import SolarData
from bonsai.bim.module.light.decorator import SolarDecorator

sun_position = tool.Blender.get_sun_position_addon()

with open(os.path.join(os.path.dirname(__file__), "spectraldb.json"), "r") as f:
    spectraldb = json.load(f)


def get_sites(self, context):
    if not SolarData.is_loaded:
        SolarData.load()
    return SolarData.data["sites"]


def update_latlong(self, context):
    update_sun_path(self)


def update_hourminute(self, context):
    update_sun_path(self)


def update_date(self, context):
    update_sun_path(self)


def update_true_north(self, context):
    update_sun_path(self)


def update_sun_path_size(self, context):
    update_sun_path(self)


def update_display_shadows(self, context):
    if self.display_shadows:
        update_sun_path(self)
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
        update_sun_path(self)
        SolarDecorator.install(bpy.context)
    else:
        SolarDecorator.uninstall()


def update_resolution(self, context):
    context.scene.render.resolution_x = self.radiance_resolution_x
    context.scene.render.resolution_y = self.radiance_resolution_y


def update_sun_path(self):
    if not SolarData.is_loaded:
        SolarData.load()

    if (sun_position := SolarData.data["sun_position"]) is None:
        return

    props = bpy.context.scene.BIMSolarProperties
    sun_props = bpy.context.scene.sun_pos_properties

    sun_props.sun_distance = self.sun_path_size
    sun_props.latitude = self.latitude
    sun_props.longitude = self.longitude
    sun_props.month = self.month
    sun_props.day = self.day
    sun_props.time = self.hour + (self.minute / 60)
    # Preserve IFC sign convention
    sun_props.north_offset = radians(self.true_north * -1)

    props.timezone = tzfpy.get_tz(props.longitude, props.latitude)
    timezone = pytz.timezone(props.timezone)
    dt = datetime.datetime(sun_props.year, sun_props.month, sun_props.day, props.hour, props.minute)
    local_time = timezone.localize(dt, is_dst=None)
    sun_props.use_daylight_savings = bool(local_time.dst())
    sun_props.UTC_zone = local_time.utcoffset().total_seconds() / 3600
    if sun_props.use_daylight_savings:
        sun_props.UTC_zone -= 1
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

    props.azimuth = azimuth
    props.elevation = elevation
    props.UTC_zone = zone

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


class RadianceMaterial(PropertyGroup):
    name: StringProperty(name="Name")
    style_id: StringProperty(name="Style ID")
    category: StringProperty(name="Category")
    subcategory: StringProperty(name="Subcategory")
    is_mapped: BoolProperty(name="Is Mapped", default=False)
    color: FloatVectorProperty(name="Color", subtype="COLOR", default=(1.0, 1.0, 1.0), min=0.0, max=1.0, size=3)


class RadianceExporterProperties(PropertyGroup):

    def update_output_dir(self, context):
        if self.output_dir:
            self.output_dir = bpy.path.abspath(self.output_dir)

    def update_ifc_file(self, context):
        if self.ifc_file:
            self.ifc_file = bpy.path.abspath(self.ifc_file)

    def add_material_mapping(self, style_id, style_name):
        item = self.materials.add()
        item.name = style_name
        item.style_id = style_id
        item.category = ""
        item.subcategory = ""
        item.color = (1.0, 1.0, 1.0)  # Default white
        return item

    def import_mappings(self, filepath):
        with open(filepath, "r") as f:
            mappings = json.load(f)

        for style_id, mapping in mappings.items():
            material = self.get_material_mapping(mapping["name"])
            if material:
                material.style_id = style_id
                material.category = mapping["category"]
                material.subcategory = mapping["subcategory"]
                material.is_mapped = True
            else:
                new_material = self.add_material_mapping(style_id, mapping["name"])
                new_material.category = mapping["category"]
                new_material.subcategory = mapping["subcategory"]
                new_material.is_mapped = True

    def get_material_mapping(self, style_name):
        return next((item for item in self.materials if item.name == style_name), None)

    def set_material_mapping(self, style_id, style_name, category, subcategory):
        item = self.get_material_mapping(style_name)
        if item:
            item.category = category
            item.subcategory = subcategory
        else:
            self.add_material_mapping(style_id, style_name)
            self.materials[-1].category = category
            self.materials[-1].subcategory = subcategory

    def get_mappings_dict(self):
        return {
            item.style_id: (item.category, item.subcategory)
            for item in self.materials
            if item.category and item.subcategory
        }

    def unmap_material(self, style_name):
        item = self.get_material_mapping(style_name)
        if item:
            item.category = ""
            item.subcategory = ""
            item.is_mapped = False

    is_exporting: bpy.props.BoolProperty(
        name="Is Exporting", description="Whether the OBJ export is in progress", default=False
    )

    categories = [
        ("Wall", "Wall", ""),
        ("Floor", "Floor", ""),
        ("Ceiling", "Ceiling", ""),
        ("Door", "Door", ""),
        ("Furniture", "Furniture", ""),
        ("Exterior Floor", "Exterior Floor", ""),
        ("Others", "Others", ""),
        ("Exterior Building", "Exterior Building", ""),
        ("Window Mullion", "Window Mullion", ""),
        ("PV", "PV", ""),
        ("Plant", "Plant", ""),
        ("Exterior", "Exterior", ""),
        ("Color Swatch", "Color Swatch", ""),
        ("Glass", "Glass", ""),
    ]

    def update_material_mapping(self, context):
        if self.active_material_index >= 0 and self.active_material_index < len(self.materials):
            active_material = self.materials[self.active_material_index]
            active_material.category = self.category
            active_material.subcategory = self.subcategory
            active_material.is_mapped = True
            print(f"Material '{active_material.name}' mapped to {self.category} - {self.subcategory}")

    category: bpy.props.EnumProperty(
        items=categories, name="Category", description="Material category", update=update_material_mapping
    )

    def get_subcategories(self, context):
        global SUBCATEGORIES_ENUM_ITEMS
        if self.category in spectraldb:
            SUBCATEGORIES_ENUM_ITEMS = [(k, k, "") for k in spectraldb[self.category].keys()]
        else:
            SUBCATEGORIES_ENUM_ITEMS = []
        return SUBCATEGORIES_ENUM_ITEMS

    subcategory: bpy.props.EnumProperty(
        items=get_subcategories, name="Subcategory", description="Material subcategory", update=update_material_mapping
    )

    materials: CollectionProperty(type=RadianceMaterial)
    active_material_index: IntProperty()

    # material_mappings: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="Material Mappings")
    # material_mappings: CollectionProperty(type=MaterialMapping)

    should_load_from_memory: BoolProperty(
        name="Load from Memory",
        default=False,
    )

    radiance_resolution_x: IntProperty(
        name="X", description="Horizontal resolution of the output image", default=1920, min=1, update=update_resolution
    )
    radiance_resolution_y: IntProperty(
        name="Y", description="Vertical resolution of the output image", default=1080, min=1, update=update_resolution
    )
    output_dir: StringProperty(
        name="Output Directory",
        description="Directory to output Radiance files",
        default="",
        subtype="DIR_PATH",
        update=lambda self, context: self.update_output_dir(context),
    )
    ifc_file: StringProperty(
        name="IFC File",
        description="Path to the IFC file",
        default="",
        subtype="FILE_PATH",
        update=lambda self, context: self.update_ifc_file(context),
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
    output_file_name: StringProperty(
        name="Output File Name", description="Name of the output image file (without extension)", default="render"
    )

    output_file_format: EnumProperty(
        name="Output File Format",
        description="Format of the output image file",
        items=[
            ("HDR", "HDR + Tiff", "High Dynamic Range"),
        ],
        default="HDR",
    )

    use_hdr: BoolProperty(
        name="Use HDR",
        description="Use HDR image format",
        default=True,
    )

    choose_hdr_image: EnumProperty(
        name="HDR Image",
        description="Choose an HDR image to use",
        items=[
            ("Noon", "Noon", "Noon"),
        ],
        default="Noon",
    )

    use_active_camera: BoolProperty(
        name="Use Active Camera", description="Use the active camera in the scene", default=True
    )

    selected_camera: PointerProperty(
        type=bpy.types.Object,
        name="Camera",
        description="Select a camera to use for rendering",
        poll=lambda self, object: object.type == "CAMERA",
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
    azimuth: FloatProperty(name="Azimuth")
    elevation: FloatProperty(name="Elevation")
    UTC_zone: FloatProperty(name="UTC Zone")
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

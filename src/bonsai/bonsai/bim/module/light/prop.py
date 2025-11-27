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
from typing import TYPE_CHECKING, Literal, Union
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

sun_position = tool.Blender.get_addon("sun_position")
now = datetime.datetime.now()

with open(os.path.join(os.path.dirname(__file__), "spectraldb.json"), "r") as f:
    spectraldb: dict[str, dict[str, str]] = json.load(f)


def get_sites(self: "BIMSolarProperties", context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not SolarData.is_loaded:
        SolarData.load()
    return SolarData.data["sites"]


def update_coordinates(self: "BIMSolarProperties", context: bpy.types.Context) -> None:
    # We define our own `coordinates` property just to ensure changing it would update
    # all other props.
    # But we still need to set original prop value and retrieve it to ensure coordinate
    # was parsed correctly.
    sun_props = tool.Blender.get_sun_props()
    assert sun_props
    sun_props.coordinates = self.coordinates
    self["coordinates"] = sun_props.coordinates
    self["longitude"] = sun_props.longitude
    self["latitude"] = sun_props.latitude
    update_sun_path(self)


def update_latlong(self: "BIMSolarProperties", context: bpy.types.Context) -> None:
    sun_props = tool.Blender.get_sun_props()
    assert sun_props
    sun_props.longitude = sun_props.longitude
    sun_props.latitude = sun_props.latitude
    self["coordinates"] = sun_props.coordinates
    update_sun_path(self)


def update_shadow_mode(self: "BIMSolarProperties", context: bpy.types.Context) -> None:
    assert context.scene
    if self.shadow_mode == "SHADING":
        update_sun_path(self)
        context.scene.render.engine = "BLENDER_WORKBENCH"
        assert context.scene.display
        assert context.scene.display.shading
        context.scene.display.shading.light = "FLAT"
        context.scene.display.shading.show_shadows = True
        context.scene.display.shading.show_object_outline = True
        context.scene.display.shadow_focus = 1.0
        assert context.scene.view_settings
        context.scene.view_settings.view_transform = "Standard"  # Preserve shading colours
        space = tool.Blender.get_view3d_space()
        assert space
        space.shading.type = "RENDERED"
    elif self.shadow_mode == "RENDERING":
        sun_props = tool.Blender.get_sun_props()
        assert sun_props
        if sun_props.sun_object is None:
            light = bpy.data.lights.new(name="Sun", type="SUN")
            sun = bpy.data.objects.new("Sun", light)
            context.scene.collection.objects.link(sun)
            sun_props.sun_object = sun
        update_sun_path(self)
        context.scene.render.engine = tool.Blender.get_eevee_name()
        assert context.scene.display
        assert context.scene.display.shading
        context.scene.display.shading.light = "FLAT"
        context.scene.display.shading.show_shadows = True
        context.scene.display.shading.show_object_outline = True
        context.scene.display.shadow_focus = 1.0
        assert context.scene.view_settings
        context.scene.view_settings.view_transform = "Standard"  # Preserve shading colours
        space = tool.Blender.get_view3d_space()
        assert space
        space.shading.type = "RENDERED"
    else:
        space = tool.Blender.get_view3d_space()
        assert space
        space.shading.type = "SOLID"


def update_display_sun_path(self: "BIMSolarProperties", context: bpy.types.Context) -> None:
    if self.display_sun_path:
        update_sun_path(self)
        SolarDecorator.install(bpy.context)
    else:
        SolarDecorator.uninstall()


def update_resolution(self: "RadianceExporterProperties", context: bpy.types.Context) -> None:
    assert context.scene
    context.scene.render.resolution_x = self.radiance_resolution_x
    context.scene.render.resolution_y = self.radiance_resolution_y


def update_sun_path(self: "BIMSolarProperties", context: Union[bpy.types.Context, None] = None) -> None:
    if not SolarData.is_loaded:
        SolarData.load()

    if (sun_position := SolarData.data["sun_position"]) is None:
        return

    if TYPE_CHECKING:
        import sun_position

    props = tool.Blender.get_solar_props()
    sun_props = tool.Blender.get_sun_props()
    assert sun_props

    sun_props.sun_distance = self.sun_path_size
    sun_props.latitude = self.latitude
    sun_props.longitude = self.longitude
    sun_props.year = self.year
    sun_props.month = self.month
    sun_props.day = self.day
    sun_props.time = self.hour + (self.minute / 60)
    # Preserve IFC sign convention
    sun_props.north_offset = self.true_north * -1

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

    # Update Blender viewport light direction for shadow visualization
    # This coordinate transformation converts from sun_position addon's coordinate system
    # to Blender's display.light_direction coordinate system
    # Note: This only affects viewport shading, not the Radiance rendering
    mat = Matrix(((-1.0, 0.0, 0.0, 0.0), (0.0, 0, 1.0, 0.0), (-0.0, -1.0, 0, 0.0), (0.0, 0.0, 0.0, 1.0))).inverted()
    rotation_euler = Euler((elevation - pi / 2, 0, -azimuth))
    rotation_quaternion = rotation_euler.to_quaternion()

    props.azimuth = azimuth
    props.elevation = elevation
    props.UTC_zone = zone

    assert bpy.context.scene
    assert bpy.context.scene.display
    # Set viewport light direction based on sun position
    # If sun is below horizon (z < 0), use default upward direction
    # Otherwise, use calculated direction from sun position
    if sun_vector.z < 0:
        bpy.context.scene.display.light_direction = mat @ Vector((0, 0, 1))
    else:
        bpy.context.scene.display.light_direction = mat @ (rotation_quaternion @ Vector((0, 0, -1)))
    SolarData.data["sun"] = sun_vector

    if obj := bpy.data.objects.get("SunPathCamera"):
        assert isinstance(obj.data, bpy.types.Camera)
        obj.matrix_world.translation = sun_vector
        z180_quaternion = Quaternion((0, 0, 1), radians(180))
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = rotation_quaternion @ z180_quaternion
        obj.data.ortho_scale = props.sun_path_size * 2


class RadianceMaterial(PropertyGroup):
    style_id: StringProperty(name="Style ID")
    category: StringProperty(name="Category")
    subcategory: StringProperty(name="Subcategory")
    is_mapped: BoolProperty(name="Is Mapped", default=False)
    color: FloatVectorProperty(name="Color", subtype="COLOR", default=(1.0, 1.0, 1.0), min=0.0, max=1.0, size=3)

    if TYPE_CHECKING:
        style_id: str
        category: str
        subcategory: str
        is_mapped: bool
        color: tuple[float, float, float]


class IESLight(PropertyGroup):
    """Represents a mapping between an IES light file and a scene Empty object."""

    ies_file_path: StringProperty(
        name="IES File Path",
        description="Path to the IES luminaire data file",
        subtype="FILE_PATH",
        default="",
    )
    target_object: PointerProperty(
        type=bpy.types.Object,
        name="Target Object",
        description="Empty object where the light fixture will be placed",
        poll=lambda self, obj: obj.type == "EMPTY",
    )
    rotation_z: FloatProperty(
        name="Rotation Z",
        description="Rotation around Z-axis in degrees (-180 to 180)",
        min=-180.0,
        max=180.0,
        default=0.0,
        subtype="ANGLE",
    )
    is_enabled: BoolProperty(
        name="Enabled",
        description="Include this light in the Radiance export",
        default=True,
    )

    # Additional lamp properties for customization
    lamp_type: StringProperty(
        name="Lamp Type",
        description="Type of lamp (e.g., 'LED', 'metal halide', 'fluorescent')",
        default="",
    )
    lamp_color: FloatVectorProperty(
        name="Lamp Color",
        description="Lamp color (RGB) for custom color adjustments",
        subtype="COLOR",
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        size=3,
    )
    multiply_factor: FloatProperty(
        name="Brightness Factor",
        description="Multiply all output quantities by this factor (0.1 to 10.0)",
        min=0.1,
        max=10.0,
        default=1.0,
    )
    radius: FloatProperty(
        name="Illum Sphere Radius",
        description="Radius of illum sphere (ignores geometry from IES file). 0 = use IES geometry",
        min=0.0,
        max=10.0,
        default=0.0,
    )

    if TYPE_CHECKING:
        ies_file_path: str
        target_object: Union[bpy.types.Object, None]
        rotation_z: float
        is_enabled: bool
        lamp_type: str
        lamp_color: tuple[float, float, float]
        multiply_factor: float
        radius: float


class RadianceExporterProperties(PropertyGroup):

    def update_output_dir(self, context) -> None:
        if self.output_dir:
            self.output_dir = bpy.path.abspath(self.output_dir)

    def update_ifc_file(self, context) -> None:
        if self.ifc_file:
            self.ifc_file = bpy.path.abspath(self.ifc_file)

    def get_categories(self, context):
        return sorted([(k, k, "") for k in spectraldb.keys()])

    def add_material_mapping(self, style_id: str, style_name: str) -> RadianceMaterial:
        item = self.materials.add()
        item.name = style_name
        item.style_id = style_id
        item.category = ""
        item.subcategory = ""
        item.color = (1.0, 1.0, 1.0)  # Default white
        return item

    def import_mappings(self, filepath: str) -> None:
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

    def get_material_mapping(self, style_name: str) -> Union[RadianceMaterial, None]:
        return next((item for item in self.materials if item.name == style_name), None)

    def set_material_mapping(self, style_id: str, style_name: str, category: str, subcategory: str) -> None:
        item = self.get_material_mapping(style_name)
        if item:
            item.category = category
            item.subcategory = subcategory
        else:
            self.add_material_mapping(style_id, style_name)
            self.materials[-1].category = category
            self.materials[-1].subcategory = subcategory

    def get_mappings_dict(self) -> dict[str, tuple[str, str]]:
        return {
            item.style_id: (item.category, item.subcategory)
            for item in self.materials
            if item.category and item.subcategory
        }

    def unmap_material(self, style_name: str) -> None:
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

    def update_material_mapping(self, context: bpy.types.Context) -> None:
        if self.active_material_index >= 0 and self.active_material_index < len(self.materials):
            active_material = self.materials[self.active_material_index]
            active_material.category = self.category
            active_material.subcategory = self.subcategory
            active_material.is_mapped = True
            print(f"Material '{active_material.name}' mapped to {self.category} - {self.subcategory}")

    category: bpy.props.EnumProperty(
        items=get_categories, name="Category", description="Material category", update=update_material_mapping
    )

    def get_subcategories(self, context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
        if self.category in spectraldb:
            return sorted([(k, k, "") for k in spectraldb[self.category].keys()])
        return []

    subcategory: bpy.props.EnumProperty(
        items=get_subcategories, name="Subcategory", description="Material subcategory", update=update_material_mapping
    )

    materials: CollectionProperty(type=RadianceMaterial)
    active_material_index: IntProperty()

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
            ("HDR", "HDR", "High Dynamic Range (HDR) file only"),
            ("HDR_TIFF", "HDR + Tiff", "High Dynamic Range (HDR) and Tiff files"),
        ],
        default="HDR_TIFF",
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

    use_sun: BoolProperty(
        name="Use Sun",
        description="Use sun position data to generate sky. If disabled, generates a default sky without sun",
        default=True,
    )

    # Sky generation parameters
    sky_condition: EnumProperty(
        name="Sky Condition",
        description="Type of sky condition to generate",
        items=[
            ("SUNNY_WITH_SUN", "Sunny with Sun", "Clear sky with direct sun"),
            ("SUNNY_WITHOUT_SUN", "Sunny without Sun", "Clear sky without direct sun"),
            ("CLOUDY", "Cloudy", "Overcast sky condition"),
        ],
        default="SUNNY_WITH_SUN",
    )

    ground_reflectance: FloatProperty(
        name="Ground Reflectance",
        description="Ground reflectance value (0.0 to 1.0)",
        min=0.0,
        max=1.0,
        default=0.2,
    )

    turbidity: FloatProperty(
        name="Turbidity",
        description="Atmospheric turbidity (1.0 to 10.0). Lower values = clearer sky",
        min=1.0,
        max=10.0,
        default=3.0,
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

    ies_lights: CollectionProperty(
        type=IESLight,
        name="IES Lights",
        description="Collection of IES light fixtures mapped to scene objects",
    )
    active_ies_light_index: IntProperty(
        name="Active IES Light Index",
        description="Index of the active IES light in the collection",
        default=-1,
    )

    # False color analysis properties
    use_false_color: BoolProperty(
        name="Generate False Color Image",
        description="Generate a false color HDR image for illuminance analysis",
        default=False,
    )

    false_color_label: EnumProperty(
        name="Legend Label Unit",
        description="Unit for the false color legend",
        items=[
            ("fc", "Foot-Candles", "US lighting standard unit"),
            ("lux", "Lux", "International lighting standard unit"),
            ("cd/m2", "Candela per m²", "Luminance unit"),
        ],
        default="fc",
    )

    false_color_scale: FloatProperty(
        name="Scale Factor",
        description="Maximum scale value for the false color legend",
        min=0.1,
        max=100.0,
        default=3.0,
    )

    false_color_contour_lines: BoolProperty(
        name="Enable Contour Lines",
        description="Add contour lines to the false color image",
        default=True,
    )

    false_color_contour_mode: EnumProperty(
        name="Contour Mode",
        description="Contour line display mode",
        items=[
            (
                "WITH_BG",
                "Contour Lines with Background",
                "Show contour lines overlaid on the colored false color background",
            ),
            ("WITHOUT_BG", "Contour Lines Only", "Show only contour lines without the false color background"),
        ],
        default="WITH_BG",
    )

    false_color_multiplier: FloatProperty(
        name="Multiplier",
        description="Conversion multiplier (179.0 for lux, 16.6295 for foot-candles)",
        min=0.1,
        max=1000.0,
        default=16.629505759940542,
    )

    false_color_output_name: StringProperty(
        name="False Color Output Name",
        description="Name of the false color output file (without extension)",
        default="false_color",
    )

    if TYPE_CHECKING:
        is_exporting: bool
        category: str
        subcategory: str
        materials: bpy.types.bpy_prop_collection_idprop[RadianceMaterial]
        active_material_index: int
        should_load_from_memory: bool
        radiance_resolution_x: int
        radiance_resolution_y: int
        output_dir: str
        ifc_file: str
        radiance_quality: Literal["LOW", "MEDIUM", "HIGH"]
        radiance_detail: Literal["LOW", "MEDIUM", "HIGH"]
        radiance_variability: Literal["LOW", "MEDIUM", "HIGH"]
        output_file_name: str
        output_file_format: Literal["HDR"]
        use_hdr: bool
        choose_hdr_image: Literal["Noon"]
        use_sun: bool
        sky_condition: Literal["SUNNY_WITH_SUN", "SUNNY_WITHOUT_SUN", "CLOUDY"]
        ground_reflectance: float
        turbidity: float
        use_active_camera: bool
        selected_camera: Union[bpy.types.Object, None]
        ies_lights: bpy.types.bpy_prop_collection_idprop[IESLight]
        active_ies_light_index: int
        use_false_color: bool
        false_color_label: Literal["fc", "lux", "cd/m2"]
        false_color_scale: float
        false_color_contour_lines: bool
        false_color_contour_mode: Literal["WITH_BG", "WITHOUT_BG"]
        false_color_multiplier: float
        false_color_output_name: str


class BIMSolarProperties(PropertyGroup):
    sites: EnumProperty(items=get_sites, name="Sites")
    coordinates: StringProperty(
        name="Coordinates",
        description="Latitude and longitude on Earth. Coordinates can be directly entered from an online map",
        update=update_coordinates,
        default="33°51′54.51″S 151°12′35.64″E",
    )
    latitude: FloatProperty(
        name="Latitude",
        min=-90,
        max=90,
        update=update_latlong,
        default=-33.865143,
    )
    longitude: FloatProperty(
        name="Longitude",
        min=-180,
        max=180,
        update=update_latlong,
        default=151.209900,
    )
    timezone: StringProperty(name="Timezone", default="Etc/GMT")
    true_north: FloatProperty(name="True North", min=-pi, max=pi, subtype="ANGLE", update=update_sun_path)
    year: IntProperty(name="Year", min=1, max=9999, default=now.year, update=update_sun_path)
    month: IntProperty(name="Month", min=1, max=12, default=now.month, update=update_sun_path)
    day: IntProperty(name="Date", min=1, max=31, default=now.day, update=update_sun_path)
    hour: IntProperty(name="Hour", min=0, max=23, default=now.hour, update=update_sun_path)
    minute: IntProperty(name="Minute", min=0, max=59, default=now.minute, update=update_sun_path)
    sun_position: FloatVectorProperty(name="Sun Position", subtype="XYZ", default=(0, 0, 0))
    sun_path_origin: FloatVectorProperty(name="Sun Path Origin", subtype="XYZ", default=(0, 0, 0))
    sun_path_size: FloatProperty(name="Sun Path Size", min=0.1, default=50, update=update_sun_path)
    azimuth: FloatProperty(name="Azimuth")
    elevation: FloatProperty(name="Elevation")
    UTC_zone: FloatProperty(name="UTC Zone")
    shadow_mode: bpy.props.EnumProperty(
        items=(
            ("NONE", "No Shadows", "No shadows"),
            (
                "SHADING",
                "Shaded",
                "Fast shadows sufficient for external shadow analysis based on shading styles",
                "SHADING_SOLID",
                1,
            ),
            (
                "RENDERING",
                "Rendered",
                "Raycast (Eevee) shadows considering transparency based on rendering styles",
                "SHADING_RENDERED",
                2,
            ),
        ),
        name="Shadow Mode",
        description="How to display shadows in the scene",
        update=update_shadow_mode,
    )
    display_sun_path: BoolProperty(
        name="Display Sun Path",
        default=False,
        description="Displays analemmas and sun position",
        update=update_display_sun_path,
    )

    if TYPE_CHECKING:
        sites: str
        coordinates: str
        latitude: float
        longitude: float
        timezone: str
        true_north: float
        year: int
        month: int
        day: int
        hour: int
        minute: int
        sun_position: Vector
        sun_path_origin: Vector
        sun_path_size: float
        azimuth: float
        elevation: float
        UTC_zone: float
        shadow_mode: Literal["NONE", "SHADING", "RENDERING"]
        display_sun_path: bool

    def set_from_datetime(self, dt: datetime.datetime) -> None:
        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.hour = dt.hour
        self.minute = dt.minute

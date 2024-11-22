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
import ifcopenshell.util.geolocation
import bonsai.tool as tool
from bonsai.bim.prop import Attribute
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
from bonsai.bim.module.georeference.data import GeoreferenceData
from bonsai.bim.module.georeference.decorator import GeoreferenceDecorator


def get_coordinate_operation_class(self, context):
    if not GeoreferenceData.is_loaded:
        GeoreferenceData.load()
    return GeoreferenceData.data["coordinate_operation_class"]


def update_true_north_angle(self, context):
    if self.is_changing_angle:
        return
    self.is_changing_angle = True
    try:
        x, y = ifcopenshell.util.geolocation.angle2yaxis(float(self.true_north_angle))
        self.true_north_abscissa = str(x)
        self.true_north_ordinate = str(y)
    except:
        pass
    self.is_changing_angle = False


def update_true_north_vector(self, context):
    if self.is_changing_angle:
        return
    self.is_changing_angle = True
    try:
        x = float(self.true_north_abscissa)
        y = float(self.true_north_ordinate)
        self.true_north_angle = str(round(ifcopenshell.util.geolocation.yaxis2angle(x, y), 7))
    except:
        pass
    self.is_changing_angle = False


def update_grid_north_angle(self, context):
    if self.is_changing_angle:
        return
    self.is_changing_angle = True
    try:
        x, y = ifcopenshell.util.geolocation.angle2xaxis(float(self.grid_north_angle))
        self.x_axis_abscissa = str(x)
        self.x_axis_ordinate = str(y)
        self.x_axis_is_null = False
    except:
        pass
    self.is_changing_angle = False


def update_grid_north_vector(self, context):
    if self.is_changing_angle:
        return
    self.is_changing_angle = True
    try:
        x = float(self.x_axis_abscissa)
        y = float(self.x_axis_ordinate)
        self.grid_north_angle = str(round(ifcopenshell.util.geolocation.xaxis2angle(x, y), 7))
        self.x_axis_is_null = False
    except:
        pass
    self.is_changing_angle = False


def update_should_visualise(self, context):
    if self.should_visualise:
        GeoreferenceDecorator.install(bpy.context)
    else:
        GeoreferenceDecorator.uninstall()


def update_blender_coordinates(self, context):
    props = bpy.context.scene.BIMGeoreferenceProperties
    if props.is_updating_coordinates:
        return
    props.is_updating_coordinates = True
    blender_coordinates = tool.Georeference.get_coordinates("blender")
    local_coordinates = ifcopenshell.util.geolocation.xyz2enh(
        *blender_coordinates,
        float(props.blender_offset_x),
        float(props.blender_offset_y),
        float(props.blender_offset_z),
        float(props.blender_x_axis_abscissa),
        float(props.blender_x_axis_ordinate),
    )
    tool.Georeference.set_coordinates("local", local_coordinates)
    tool.Georeference.set_coordinates(
        "map", ifcopenshell.util.geolocation.auto_xyz2enh(tool.Ifc.get(), *local_coordinates)
    )
    props.is_updating_coordinates = False


def update_local_coordinates(self, context):
    props = bpy.context.scene.BIMGeoreferenceProperties
    if props.is_updating_coordinates:
        return
    props.is_updating_coordinates = True
    local_coordinates = tool.Georeference.get_coordinates("local")
    tool.Georeference.set_coordinates(
        "map", ifcopenshell.util.geolocation.auto_xyz2enh(tool.Ifc.get(), *local_coordinates)
    )
    if props.has_blender_offset:
        tool.Georeference.set_coordinates(
            "blender",
            ifcopenshell.util.geolocation.enh2xyz(
                *local_coordinates,
                float(props.blender_offset_x),
                float(props.blender_offset_y),
                float(props.blender_offset_z),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
            ),
        )
    props.is_updating_coordinates = False


def update_map_coordinates(self, context):
    props = bpy.context.scene.BIMGeoreferenceProperties
    if props.is_updating_coordinates:
        return
    props.is_updating_coordinates = True
    map_coordinates = tool.Georeference.get_coordinates("map")
    local_coordinates = ifcopenshell.util.geolocation.auto_enh2xyz(tool.Ifc.get(), *map_coordinates)
    tool.Georeference.set_coordinates("local", local_coordinates)
    if props.has_blender_offset:
        tool.Georeference.set_coordinates(
            "blender",
            ifcopenshell.util.geolocation.enh2xyz(
                *local_coordinates,
                float(props.blender_offset_x),
                float(props.blender_offset_y),
                float(props.blender_offset_z),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
            ),
        )
    props.is_updating_coordinates = False


class BIMGeoreferenceProperties(PropertyGroup):
    coordinate_operation_class: bpy.props.EnumProperty(
        items=get_coordinate_operation_class, name="Coordinate Operation Class"
    )
    is_changing_angle: BoolProperty(name="Is Changing Angle", default=False)
    is_editing: BoolProperty(name="Is Editing")
    is_editing_wcs: BoolProperty(name="Is Editing WCS")
    is_editing_true_north: BoolProperty(name="Is Editing True North")
    coordinate_operation: CollectionProperty(name="Coordinate Operation", type=Attribute)
    projected_crs: CollectionProperty(name="Projected CRS", type=Attribute)
    is_updating_coordinates: BoolProperty(name="Is Updating Coordinates", default=False)
    blender_coordinates: StringProperty(
        name="Blender Coordinates",
        description='Formatted "x,y,z" (without quotes)',
        default="0,0,0",
        update=update_blender_coordinates,
    )
    local_coordinates: StringProperty(
        name="Local Coordinates",
        description='Formatted "x,y,z" (without quotes)',
        default="0,0,0",
        update=update_local_coordinates,
    )
    map_coordinates: StringProperty(
        name="Map Coordinates",
        description='Formatted "x,y,z" (without quotes)',
        default="0,0,0",
        update=update_map_coordinates,
    )
    should_visualise: BoolProperty(
        name="Should Visualise",
        description="Displays a visualisation of all georeferencing data at the origin",
        default=False,
        update=update_should_visualise,
    )
    visualization_scale: IntProperty(name="Visualization Scale", description="Affects the georeference decorator size", default=1, min=1, max=20)
    grid_north_angle: StringProperty(name="Grid North Angle", update=update_grid_north_angle)
    x_axis_abscissa: StringProperty(name="X Axis Abscissa", update=update_grid_north_vector)
    x_axis_ordinate: StringProperty(name="X Axis Ordinate", update=update_grid_north_vector)
    x_axis_is_null: BoolProperty(name="X Axis Is Null")

    # These are only for reference to capture data about a host model from a linked model
    # If you relink a model from a new host origin, we can autodetect it in theory with this
    host_model_origin: StringProperty(name="Host Model Origin")
    host_model_origin_si: StringProperty(name="Host Model Origin SI")
    host_model_project_north: StringProperty(name="Host Model Angle to Grid North")

    # This is the ENH in project units and SI units of the Blender session's 0,0,0.
    # These are only for reference, using tool.Georeference.set_model_origin on
    # project load, project create, and when linking for the first time from an
    # empty Blender session.
    model_origin: StringProperty(name="Model Origin")
    model_origin_si: StringProperty(name="Model Origin SI")
    model_project_north: StringProperty(name="Model Angle to Grid North")

    # True if there is a temporary Blender session coordinate system
    has_blender_offset: BoolProperty(name="Has Blender Offset")

    # These are the helmert transformation parameters of the Blender session
    blender_offset_x: StringProperty(name="Blender Offset X", default="0")
    blender_offset_y: StringProperty(name="Blender Offset Y", default="0")
    blender_offset_z: StringProperty(name="Blender Offset Z", default="0")
    blender_x_axis_abscissa: StringProperty(name="Blender X Axis Abscissa", default="1")
    blender_x_axis_ordinate: StringProperty(name="Blender X Axis Ordinate", default="0")

    true_north_angle: StringProperty(name="True North Angle", update=update_true_north_angle)
    true_north_abscissa: StringProperty(name="True North Abscissa", update=update_true_north_vector)
    true_north_ordinate: StringProperty(name="True North Ordinate", update=update_true_north_vector)
    wcs_x: StringProperty(name="WCS X", default="0")
    wcs_y: StringProperty(name="WCS Y", default="0")
    wcs_z: StringProperty(name="WCS Z", default="0")
    wcs_rotation: StringProperty(name="WCS Rotation", default="0")

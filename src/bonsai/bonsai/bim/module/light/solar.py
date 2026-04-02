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

from datetime import datetime
from math import radians
from typing import TYPE_CHECKING

import bpy
import ifcopenshell
import ifcopenshell.util.geolocation
import requests
import webbrowser

import bonsai.tool as tool
from bonsai.bim.module.light.data import SolarData


class ImportTrueNorth(bpy.types.Operator):
    bl_idname = "bim.import_true_north"
    bl_label = "Import True North"
    bl_description = "Imports the True North from your IFC geometric context"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            return False
        if not SolarData.is_loaded:
            SolarData.load()
        return SolarData.data["true_north"] is not None

    def execute(self, context):
        props = tool.Blender.get_solar_props()
        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            value = context.TrueNorth.DirectionRatios
            props.true_north = radians(ifcopenshell.util.geolocation.yaxis2angle(*value[:2]))
        return {"FINISHED"}


class ImportLatLong(bpy.types.Operator):
    bl_idname = "bim.import_lat_long"
    bl_label = "Import Latitude / Longitude"
    bl_description = "Imports the latitude / longitude from an IfcSite"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Blender.get_solar_props()
        site = tool.Ifc.get().by_id(int(props.sites))
        if site.RefLatitude and site.RefLongitude:
            props.latitude = ifcopenshell.util.geolocation.dms2dd(*site.RefLatitude)
            props.longitude = ifcopenshell.util.geolocation.dms2dd(*site.RefLongitude)
        return {"FINISHED"}


class MoveSunPathTo3DCursor(bpy.types.Operator):
    bl_idname = "bim.move_sun_path_to_3d_cursor"
    bl_label = "Move Sun Path To 3D Cursor"
    bl_description = "Shifts the visualisation of the Sun Path to the 3D cursor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Blender.get_solar_props()
        assert context.scene
        props.sun_path_origin = context.scene.cursor.location
        tool.Blender.update_viewport()
        return {"FINISHED"}


class ViewFromSun(bpy.types.Operator):
    bl_idname = "bim.view_from_sun"
    bl_label = "View From Sun"
    bl_description = "Views your model as if you were looking from the perspective of the sun"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not (camera := bpy.data.objects.get("SunPathCamera")):
            camera = bpy.data.objects.new("SunPathCamera", bpy.data.cameras.new("SunPathCamera"))
            assert isinstance(camera.data, bpy.types.Camera)
            assert context.scene
            camera.data.type = "ORTHO"
            camera.data.ortho_scale = 100  # The default of 6m is too small
            context.scene.collection.objects.link(camera)
        tool.Blender.activate_camera(camera)
        props = tool.Blender.get_solar_props()
        props.hour = props.hour  # Just to refresh camera position
        return {"FINISHED"}


class LightPickCoordinates(bpy.types.Operator):
    bl_idname = "bim.light_pick_coordinates"
    bl_label = "Pick Coordinates"
    bl_description = (
        "Open web browser with Google Maps to pick coordinates (Right Mouse Click in maps to copy selected location).\n\n"
        "ALT+Click to insert current location based on the current IP-address (using ip-api.com)."
    )
    bl_options = {"REGISTER", "UNDO"}

    use_current_location: bpy.props.BoolProperty(options={"SKIP_SAVE"})  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        use_current_location: bool

    def invoke(self, context, event):
        if event.alt:
            self.use_current_location = True
        return self.execute(context)

    def execute(self, context):
        props = tool.Blender.get_solar_props()
        if not self.use_current_location:
            zoom = 13.5
            url = f"https://www.google.com/maps/@{props.latitude},{props.longitude},{zoom}z"
            webbrowser.open(url)
            return {"FINISHED"}

        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        props.latitude = data["lat"]
        props.longitude = data["lon"]
        return {"FINISHED"}


class LightSetTimeToNow(bpy.types.Operator):
    bl_idname = "bim.light_set_time_to_now"
    bl_label = "Now"
    bl_description = "Set time to current local time."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Blender.get_solar_props()
        props.set_from_datetime(datetime.now())
        return {"FINISHED"}

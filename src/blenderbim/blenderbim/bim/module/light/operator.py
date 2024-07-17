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

import os
import bpy
import json
import shutil
import multiprocessing
import pyradiance as pr
import ifcopenshell
import ifcopenshell.geom
import blenderbim.tool as tool
from pathlib import Path
from typing import Union
from blenderbim.bim.module.light.data import SolarData


class ExportOBJ(bpy.types.Operator):
    """Exports the IFC File to OBJ"""

    bl_idname = "export_scene.radiance"
    bl_label = "Export"
    bl_description = "Export the IFC to OBJ"

    def execute(self, context):
        # Get the resolution from the user input
        resolution_x, resolution_y = self.getResolution(context)
        quality = context.scene.radiance_exporter_properties.radiance_quality.upper()
        detail = context.scene.radiance_exporter_properties.radiance_detail.upper()
        variability = context.scene.radiance_exporter_properties.radiance_variability.upper()

        # Calculate the aspect ratio
        aspect_ratio = resolution_x / resolution_y

        # Get the blend file path and create the "Radiance Rendering" directory
        self.report({"INFO"}, "Exporting Radiance files...")
        blend_file_path = bpy.data.filepath
        if not blend_file_path:
            self.report({"ERROR"}, "Please save the Blender file before exporting.")
            return {"CANCELLED"}

        blend_file_dir = os.path.dirname(blend_file_path)
        radiance_dir = os.path.join(blend_file_dir, "RadianceRendering")

        self.report({"INFO"}, "Radiance directory: {}".format(radiance_dir))

        if not os.path.exists(radiance_dir):
            os.makedirs(radiance_dir)

        # IFC file export and processing
        settings = ifcopenshell.geom.settings()
        # Settings for obj

        serializer_settings = ifcopenshell.geom.serializer_settings()

        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.SURFACES_AND_SOLIDS)
        settings.set("apply-default-materials", True)
        serializer_settings.set("use-element-guids", True)
        settings.set("use-world-coords", True)

        ifc_file_name = context.scene.radiance_exporter_properties.ifc_file_name
        ifc_file_path = os.path.join(blend_file_dir, f"{ifc_file_name}.ifc")

        if not os.path.exists(ifc_file_path):
            self.report({"ERROR"}, f"IFC file not found: {ifc_file_path}")
            return {"CANCELLED"}

        ifc_file = ifcopenshell.open(ifc_file_path)
        for material in ifc_file.by_type("IfcMaterial"):
            self.report({"INFO"}, f"Material: {material.Name}, ID: {material.id()}")

        obj_file_path = os.path.join(radiance_dir, "model.obj")
        mtl_file_path = os.path.join(radiance_dir, "model.mtl")

        # serialiser = ifcopenshell.geom.serializers.obj(obj_file_path, mtl_file_path, settings, ifcopenshell.geom.serializer_settings())
        serialiser = ifcopenshell.geom.serializers.obj(obj_file_path, mtl_file_path, settings, serializer_settings)
        serialiser.setFile(ifc_file)
        serialiser.setUnitNameAndMagnitude("METER", 1.0)
        serialiser.writeHeader()

        iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
        if iterator.initialize():
            while True:
                serialiser.write(iterator.get())
                if not iterator.next():
                    break
        serialiser.finalize()

        return {"FINISHED"}

    def getResolution(self, context):
        scene = context.scene
        props = scene.radiance_exporter_properties
        resolution_x = props.radiance_resolution_x
        resolution_y = props.radiance_resolution_y
        return resolution_x, resolution_y


class RadianceRender(bpy.types.Operator):
    """Radiance Rendering"""

    bl_idname = "render_scene.radiance"
    bl_label = "Render"
    bl_description = "Renders the scene using Radiance"

    def execute(self, context):
        if pr is None:
            self.report({"ERROR"}, "PyRadiance is not available. Cannot perform rendering.")
            return {"CANCELLED"}

        # Get the resolution from the user input
        resolution_x, resolution_y = self.getResolution(context)
        quality = context.scene.radiance_exporter_properties.radiance_quality.upper()
        detail = context.scene.radiance_exporter_properties.radiance_detail.upper()
        variability = context.scene.radiance_exporter_properties.radiance_variability.upper()

        # Get the blend file path and create the "Radiance Rendering" directory
        blend_file_path = bpy.data.filepath
        if not blend_file_path:
            self.report({"ERROR"}, "Please save the Blender file before rendering.")
            return {"CANCELLED"}

        blend_file_dir = os.path.dirname(blend_file_path)
        radiance_dir = os.path.join(blend_file_dir, "RadianceRendering")

        # Material processing
        style = []
        obj_file_path = os.path.join(radiance_dir, "model.obj")
        with open(obj_file_path, "r") as obj_file:
            for line in obj_file:
                if line.startswith("usemtl"):
                    l = line.strip().split(" ")
                    style.append(l[1])

        # json_file_path = os.path.join(blend_file_dir, "material_mapping.json")

        json_file_path = context.scene.radiance_exporter_properties.json_file_path
        self.report({"INFO"}, f"Selected JSON file: {json_file_path}")
        if json_file_path:
            # self.report({'INFO'}, f"Selected JSON file: {json_file_name}")
            json_dest_path = os.path.join(blend_file_dir, json_file_path.split("\\")[-1])
            shutil.copy(json_file_path, json_dest_path)
            self.report({"INFO"}, f"JSON file saved to: {json_dest_path}")
        else:
            self.report({"WARNING"}, "No JSON file selected")

        with open(json_file_path, "r") as file:
            data = json.load(file)

        # Create materials.rad file
        materials_file = os.path.join(radiance_dir, "materials.rad")
        with open(materials_file, "w") as file:
            file.write("void plastic white\n0\n0\n5 1 1 1 0 0\n")
            file.write("void plastic blue_plastic\n0\n0\n5 0.1 0.2 0.8 0.05 0.1\n")
            file.write("void plastic red_plastic\n0\n0\n5 0.8 0.1 0.2 0.05 0.1\n")
            file.write("void metal silver_metal\n0\n0\n5 0.8 0.8 0.8 0.9 0.1\n")
            file.write("void glass clear_glass\n0\n0\n3 0.96 0.96 0.96\n")
            file.write("void light white_light\n0\n0\n3 1.0 1.0 1.0\n")
            file.write("void trans olive_trans\n0\n0\n7 0.6 0.7 0.4 0.05 0.05 0.7 0.2\n")

            for i in set(style):
                file.write("inherit alias " + i + " " + data.get(i, "white") + "\n")

        self.report({"INFO"}, "Exported Materials Rad file to: {}".format(materials_file))

        # Run obj2mesh
        rtm_file_path = os.path.join(radiance_dir, "model.rtm")
        mesh_file_path = save_obj2mesh_output(obj_file_path, rtm_file_path, matfiles=[materials_file])
        # subprocess.run(["obj2mesh", "-a", materials_file, obj_file_path, rtm_file_path])
        self.report({"INFO"}, "obj2mesh output: {}".format(mesh_file_path))
        scene_file = os.path.join(radiance_dir, "scene.rad")
        with open(scene_file, "w") as file:
            file.write("void mesh model\n1 " + rtm_file_path + "\n0\n0\n")

        self.report({"INFO"}, "Exported Scene file to: {}".format(scene_file))

        # Py Radiance Rendering code
        scene = pr.Scene("ascene")

        material_path = os.path.join(radiance_dir, "materials.rad")
        scene_path = os.path.join(radiance_dir, "scene.rad")

        scene.add_material(material_path)
        scene.add_surface(scene_path)

        aview = pr.View(position=(1, 1.5, 1), direction=(1, 0, 0))
        scene.add_view(aview)

        octpath = os.path.join(blend_file_dir, "ascene.oct")
        print("Reached here")
        image = pr.render(
            scene,
            ambbounce=1,
            resolution=(resolution_x, resolution_y),
            quality=quality,
            detail=detail,
            variability=variability,
        )

        raw_hdr_path = os.path.join(radiance_dir, "raw.hdr")
        with open(raw_hdr_path, "wb") as wtr:
            wtr.write(image)

        self.report({"INFO"}, "Radiance rendering completed. Output: {}".format(raw_hdr_path))
        return {"FINISHED"}

    def getResolution(self, context):
        scene = context.scene
        props = scene.radiance_exporter_properties
        resolution_x = props.radiance_resolution_x
        resolution_y = props.radiance_resolution_y
        return resolution_x, resolution_y


def save_obj2mesh_output(inp: Union[bytes, str, Path], output_file: str, **kwargs):
    output_bytes = pr.obj2mesh(inp, **kwargs)

    with open(output_file, "wb") as f:
        f.write(output_bytes)
    return output_file


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
        props = context.scene.BIMSolarProperties
        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            value = context.TrueNorth.DirectionRatios
            props.true_north = ifcopenshell.util.geolocation.yaxis2angle(*value[:2])
        return {"FINISHED"}


class ImportLatLong(bpy.types.Operator):
    bl_idname = "bim.import_lat_long"
    bl_label = "Import Latitude / Longitude"
    bl_description = "Imports the latitude / longitude from an IfcSite"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMSolarProperties
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
        props = context.scene.BIMSolarProperties
        props.sun_path_origin = bpy.context.scene.cursor.location
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
            camera.data.type = "ORTHO"
            camera.data.ortho_scale = 100  # The default of 6m is too small
            bpy.context.scene.collection.objects.link(camera)
        tool.Blender.activate_camera(camera)
        props = context.scene.BIMSolarProperties
        props.hour = props.hour  # Just to refresh camera position
        return {"FINISHED"}

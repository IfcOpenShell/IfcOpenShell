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

try:
    import pyradiance as pr
except ImportError:
    print("PyRadiance is not available. Rendering functionality will be disabled.")
    pr = None

import bpy
import blenderbim.tool as tool
from pathlib import Path
from typing import Union, Optional, Sequence
import json
import ifcopenshell
import ifcopenshell.geom
import multiprocessing
from mathutils import Vector
from blenderbim.bim.module.light.data import SolarData

ifc_materials = []


class ExportOBJ(bpy.types.Operator):
    """Exports the IFC File to OBJ"""

    bl_idname = "export_scene.radiance"
    bl_label = "Export"
    bl_description = "Export the IFC to OBJ"

    def execute(self, context):

        # Get the output directory
        should_load_from_memory = context.scene.radiance_exporter_properties.should_load_from_memory
        output_dir = context.scene.radiance_exporter_properties.output_dir

        context.scene.radiance_exporter_properties.is_exporting = True

        # Conversion from IFC to OBJ
        # Settings for obj
        settings = ifcopenshell.geom.settings()
        serializer_settings = ifcopenshell.geom.serializer_settings()

        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.SURFACES_AND_SOLIDS)
        settings.set("apply-default-materials", True)
        serializer_settings.set("use-element-guids", True)
        settings.set("use-world-coords", True)

        if should_load_from_memory:
            ifc_file = tool.Ifc.get()

        else:
            ifc_file_path = context.scene.radiance_exporter_properties.ifc_file
            ifc_file = ifcopenshell.open(ifc_file_path)

        # for material in ifc_file.by_type("IfcMaterial"):
        #     self.report({'INFO'}, f"Material: {material.Name}, ID: {material.id()}")

        obj_file_path = os.path.join(output_dir, "model.obj")
        mtl_file_path = os.path.join(output_dir, "model.mtl")

        serialiser = ifcopenshell.geom.serializers.obj(obj_file_path, mtl_file_path, settings, serializer_settings)
        serialiser.setFile(ifc_file)
        serialiser.setUnitNameAndMagnitude("METER", 1.0)
        serialiser.writeHeader()

        if ifc_file.schema in ("IFC2X3", "IFC4"):
            elements = ifc_file.by_type("IfcElement") + ifc_file.by_type("IfcProxy")
        else:
            elements = ifc_file.by_type("IfcElement")

        elements = [e for e in elements if not e.is_a("IfcFeatureElement") or e.is_a("IfcSurfaceFeature")]

        iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count(), include=elements)
        if iterator.initialize():
            while True:
                shape = iterator.get()
                materials = shape.geometry.materials
                # print(shape.geometry)
                material_ids = shape.geometry.material_ids
                # material_names = shape.geometry.material_names
                # print(material_ids)

                for material in materials:
                    # print(material, dir(material))
                    # print(material.name)
                    ifc_materials.append(material.name)

                serialiser.write(shape)
                if not iterator.next():
                    break

        serialiser.finalize()
        context.scene.radiance_exporter_properties.is_exporting = False

        self.report({"INFO"}, "Exported OBJ file to: {}".format(obj_file_path))

        return {"FINISHED"}


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
        props = context.scene.radiance_exporter_properties
        resolution_x, resolution_y = props.radiance_resolution_x, props.radiance_resolution_y
        quality = props.radiance_quality.upper()
        detail = props.radiance_detail.upper()
        variability = props.radiance_variability.upper()
        output_dir = props.output_dir
        output_file_name = props.output_file_name
        output_file_format = props.output_file_format

        obj_file_path = os.path.join(output_dir, "model.obj")

        camera = self.get_active_camera(context)
        if camera is None:
            self.report({"ERROR"}, "No active camera found in the scene. Please add a camera and set it as active.")
            return {"CANCELLED"}

        # Get camera position and direction
        camera_position, camera_direction = self.get_camera_data(camera)

        # Material processing
        # style = []

        # with open(obj_file_path, "r") as obj_file:
        #     for line in obj_file:
        #         if line.startswith("usemtl"):
        #             l = line.strip().split(" ")
        #             style.append(l[1])

        # Check if json file is empty or not
        props = context.scene.radiance_exporter_properties

        if props.use_json_file:
            # Load data from JSON file
            with open(props.json_file, "r") as file:
                data = json.load(file)
        else:
            # Use in-UI material mappings
            data = props.get_mappings_dict()

        print(data)

        # Create materials.rad file
        materials_file = os.path.join(output_dir, "materials.rad")
        with open(materials_file, "w") as file:
            file.write("void plastic white\n0\n0\n5 0.8 0.8 0.8 0 0\n")
            file.write("void plastic blue_plastic\n0\n0\n5 0.1 0.2 0.8 0.05 0.1\n")
            file.write("void plastic red_plastic\n0\n0\n5 0.8 0.1 0.2 0.05 0.1\n")
            file.write("void metal silver_metal\n0\n0\n5 0.8 0.8 0.8 0.9 0.1\n")
            file.write("void glass clear_glass\n0\n0\n3 0.96 0.96 0.96\n")
            file.write("void light white_light\n0\n0\n3 1.0 1.0 1.0\n")
            file.write("void trans olive_trans\n0\n0\n7 0.6 0.7 0.4 0.05 0.05 0.7 0.2\n")

            for style_id, radiance_material in data.items():
                print(style_id, radiance_material)
                file.write("inherit alias " + style_id + " " + data.get(style_id, "white") + "\n")
                # file.write(f"inherit alias {style_id} {radiance_material}\n")
            # for i in set(ifc_materials):
            #     print(i)
            #     file.write("inherit alias " + i + " " + data.get(i, "white") + "\n")

        self.report({"INFO"}, "Exported Materials Rad file to: {}".format(materials_file))

        # Run obj2mesh
        rtm_file_path = os.path.join(output_dir, "model.rtm")
        mesh_file_path = save_obj2mesh_output(obj_file_path, rtm_file_path, matfiles=[materials_file])
        # subprocess.run(["obj2mesh", "-a", materials_file, obj_file_path, rtm_file_path])
        self.report({"INFO"}, "obj2mesh output: {}".format(mesh_file_path))
        scene_file = os.path.join(output_dir, "scene.rad")
        with open(scene_file, "w") as file:
            # file.write("void mesh model\n1 " + rtm_file_path + "\n0\n0\n")
            file.write('void mesh model\n1 "' + rtm_file_path + '"\n0\n0\n')

        self.report({"INFO"}, "Exported Scene file to: {}".format(scene_file))

        # Py Radiance Rendering code
        scene = pr.Scene("ascene")

        material_path = os.path.join(output_dir, "materials.rad")
        scene_path = os.path.join(output_dir, "scene.rad")

        scene.add_material(material_path)
        scene.add_surface(scene_path)

        aview = pr.View(position=camera_position, direction=camera_direction)
        scene.add_view(aview)

        image = pr.render(
            scene,
            ambbounce=1,
            resolution=(resolution_x, resolution_y),
            quality=quality,
            detail=detail,
            variability=variability,
        )

        output_path = os.path.join(output_dir, f"{output_file_name}.{output_file_format.lower()}")

        if output_file_format == "HDR":
            with open(output_path, "wb") as wtr:
                wtr.write(image)
        else:
            pass

        self.report({"INFO"}, "Radiance rendering completed. Output: {}".format(output_path))
        return {"FINISHED"}

    def get_active_camera(self, context):
        if context.scene.camera:
            return context.scene.camera
        for obj in context.scene.objects:
            if obj.type == "CAMERA":
                return obj
        return None

    def get_camera_data(self, camera):
        # Get camera position
        position = camera.matrix_world.to_translation()

        # Get camera direction
        direction = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        direction.normalize()

        return (position.x, position.y, position.z), (direction.x, direction.y, direction.z)

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


class RefreshIFCMaterials(bpy.types.Operator):
    bl_idname = "bim.refresh_ifc_materials"
    bl_label = "Refresh IFC Materials"
    bl_description = "Refresh the list of IFC materials for mapping"

    def execute(self, context):
        props = context.scene.radiance_exporter_properties
        ifc_file = tool.Ifc.get() if props.should_load_from_memory else ifcopenshell.open(props.ifc_file)

        for style in ifc_file.by_type("IfcSurfaceStyle"):
            for render_item in style.Styles:
                if render_item.is_a("IfcSurfaceStyleRendering"):
                    style_id = f"IfcSurfaceStyleRendering-{render_item.id()}"
                    style_name = style.Name or f"Unnamed Style {render_item.id()}"
                    if not props.get_material_mapping(style_name):
                        props.add_material_mapping(style_id, style_name)

        return {"FINISHED"}

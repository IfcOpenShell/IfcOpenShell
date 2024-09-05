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

import os

try:
    import pyradiance as pr
except ImportError:
    print("PyRadiance is not available. Rendering functionality will be disabled.")
    pr = None

from datetime import datetime
import bpy
import bonsai.tool as tool
from pathlib import Path
from typing import Union, Optional, Sequence
import json
import math
import time
import ifcopenshell
import webbrowser
import ifcopenshell.geom
import multiprocessing
from mathutils import Vector
from bonsai.bim.module.light.data import SolarData
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper

ifc_materials = []

with open(os.path.join(os.path.dirname(__file__), "spectraldb.json"), "r") as f:
    spectraldb = json.load(f)


class ExportOBJ(bpy.types.Operator):
    """Exports the IFC File to OBJ"""

    bl_idname = "export_scene.radiance"
    bl_label = "Export"
    bl_description = "Export the IFC to OBJ"

    @classmethod
    def poll(cls, context):
        props = context.scene.radiance_exporter_properties
        if not props.should_load_from_memory and not props.ifc_file:
            cls.poll_message_set("Select an IFC file or use 'load from memory' if it's loaded in Bonsai.")
            return False
        return True

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

        elements += ifc_file.by_type("IfcSite")
        elements = [e for e in elements if not e.is_a("IfcFeatureElement") or e.is_a("IfcSurfaceFeature")]

        iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count(), include=elements)
        if iterator.initialize():
            while True:
                shape = iterator.get()
                materials = shape.geometry.materials
                material_ids = shape.geometry.material_ids
                # material_names = shape.geometry.material_names

                for material in materials:
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

        print("Starting Radiance rendering process...")
        props = context.scene.radiance_exporter_properties
        resolution_x, resolution_y = props.radiance_resolution_x, props.radiance_resolution_y

        context.scene.render.resolution_x = resolution_x
        context.scene.render.resolution_y = resolution_y

        aspect_ratio = resolution_x / resolution_y

        quality = props.radiance_quality.upper()
        detail = props.radiance_detail.upper()
        variability = props.radiance_variability.upper()
        output_dir = props.output_dir
        output_file_name = props.output_file_name
        output_file_format = props.output_file_format
        use_hdr = props.use_hdr
        choose_hdr_image = props.choose_hdr_image

        print(f"Resolution: {resolution_x}x{resolution_y}")
        print(f"Quality: {quality}, Detail: {detail}, Variability: {variability}")
        print(f"Output directory: {output_dir}")

        if use_hdr:
            hdr_image = "noon_grass_2k.hdr"
            hdr_mask = "noon_grass_2k_mask.hdr"
            sky_map_cal = "skymap.cal"
            hdr_image_path = os.path.join(os.path.dirname(__file__), "HDRs", hdr_image)
            hdr_mask_path = os.path.join(os.path.dirname(__file__), "HDRs", hdr_mask)
            sky_map_cal_path = os.path.join(os.path.dirname(__file__), "HDRs", sky_map_cal)

        obj_file_path = os.path.join(output_dir, "model.obj")

        sun_props = context.scene.BIMSolarProperties
        sun_pos_props = context.scene.sun_pos_properties
        sky_file_path = os.path.join(output_dir, "sky.rad")
        # latitude = sun_props.latitude
        # longitude = sun_props.longitude
        # month = sun_props.month
        # day = sun_props.day
        # hour = sun_props.hour
        # minute = sun_props.minute

        # print("Sun Properties:")
        # print("Latitude: ", latitude)
        # print("Longitude: ", longitude)
        # print("Timezone: ", timezone)
        # print("Month: ", month)
        # print("Day: ", day)
        # print("Hour: ", hour)
        # print("Minute: ", minute)

        print("Setting up camera...")
        if props.use_active_camera:
            camera = context.scene.camera
        else:
            camera = props.selected_camera

        if camera is None:
            self.report({"ERROR"}, "No active camera found in the scene. Please add a camera and set it as active.")
            return {"CANCELLED"}

        # Get camera position and direction
        camera_position, camera_direction = self.get_camera_data(camera)

        print(f"Camera position: {camera_position}")
        print(f"Camera direction: {camera_direction}")

        # sun_position = tool.Blender.get_sun_position_addon()
        #     azimuth, elevation = sun_position.sun_calc.get_sun_coordinates(
        #     sun_pos_props.time,
        #     sun_pos_props.latitude,
        #     sun_pos_props.longitude,
        #     -sun_pos_props.UTC_zone,
        #     sun_pos_props.month,
        #     sun_pos_props.day,
        #     sun_pos_props.year,
        # )

        dt = datetime(sun_pos_props.year, sun_props.month, sun_props.day, sun_props.hour, sun_props.minute)

        sky_description = pr.gensky(
            dt=dt,
            # azimuth=64.1,
            # altitude=-26.6,
            latitude=sun_props.latitude,
            longitude=sun_props.longitude,
            year=sun_pos_props.year,
            timezone=-int(sun_props.UTC_zone),
            # sunny_with_sun=False,
            # sunny_without_sun=False,
            # cloudy=False,
            # ground_reflectance=0.2,
            # turbidity=3.0,
        )

        sky_description_str = sky_description.decode("utf-8")

        # Write all this to file
        # skyfunc glow sky_glow
        # 0
        # 0
        # 4 .9 .9 1.15 0

        # sky_glow source sky
        # 0
        # 0
        # 4 0 0 1 180

        # skyfunc glow ground_glow
        # 0
        # 0
        # 4 1.4 .9 .6 0

        # ground_glow source ground
        # 0
        # 0
        # 4 0 0 -1 180

        if use_hdr and choose_hdr_image == "Noon":

            with open(sky_file_path, "w") as f:
                f.write(sky_description_str)
                f.write("\n")
                # f.write("skyfunc glow sky_glow\n0\n0\n4 .9 .9 1.15 0\n")
                # f.write("sky_glow source sky\n0\n0\n4 0 0 1 180\n")
                # f.write("skyfunc glow ground_glow\n0\n0\n4 1.4 .9 .6 0\n")
                # f.write("ground_glow source ground\n0\n0\n4 0 0 -1 180\n")

                f.write(
                    '''void colorpict env_map
7 red green blue "'''
                    + hdr_image_path
                    + '''"  "'''
                    + sky_map_cal_path
                    + '''" map_u map_v
0
1 0.5
 
# This is a multiplier to colour balance the env map
# In this case, it provides a rough ground luminance from 3k-5k
env_map colorfunc env_colour
4 100 100 100 .
0
0
 
# .37 .57 1.5 is measured from a HDRI image
# It is multiplied by a factor such that grey(r,g,b) = 1
skyfunc colorfunc sky_colour
4 .64 .99 2.6 .
0
0
 
void mixpict composite
7 env_colour sky_colour grey "'''
                    + hdr_mask_path
                    + '''"  "'''
                    + sky_map_cal_path
                    + """" map_u map_v
0
2 0.5 1
 
composite glow env_map_glow
0
0
4 1 1 1 0
 
env_map_glow source sky
0
0
4 0 0 1 180
 
env_colour glow ground_glow
0
0
4 1 1 1 0
 
ground_glow source ground
0
0
4 0 0 -1 180"""
                )

        elif not use_hdr:
            with open(sky_file_path, "w") as f:
                f.write(sky_description_str)
                f.write("\n")
                # f.write("skyfunc glow sky_glow\n0\n0\n4 .9 .9 1.15 0\n")
                # f.write("sky_glow source sky\n0\n0\n4 0 0 1 180\n")
                # f.write("skyfunc glow ground_glow\n0\n0\n4 1.4 .9 .6 0\n")
                # f.write("ground_glow source ground\n0\n0\n4 0 0 -1 180\n")

        props = context.scene.radiance_exporter_properties

        data = props.get_mappings_dict()

        materials_file = os.path.join(output_dir, "materials.rad")
        written_materials = set()

        all_materials = set(ifc_materials)

        with open(materials_file, "w") as file:
            # Write default materials
            default_materials = [
                "void plastic white\n0\n0\n5 0.8 0.8 0.8 0 0\n",
                # "void plastic blue_plastic\n0\n0\n5 0.1 0.2 0.8 0.05 0.1\n",
                # "void plastic red_plastic\n0\n0\n5 0.8 0.1 0.2 0.05 0.1\n",
                # "void metal silver_metal\n0\n0\n5 0.8 0.8 0.8 0.9 0.1\n",
                # "void glass clear_glass\n0\n0\n3 0.96 0.96 0.96\n",
                # "void light white_light\n0\n0\n3 1.0 1.0 1.0\n",
                # "void trans olive_trans\n0\n0\n7 0.6 0.7 0.4 0.05 0.05 0.7 0.2\n",
            ]
            for material in default_materials:
                file.write(material)
                written_materials.add(material.split()[2])  # Add material name to written set

            for style_id in all_materials:
                material = next((m for m in props.materials if m.style_id == style_id), None)
                if material and material.is_mapped:
                    category, subcategory = material.category, material.subcategory
                    if category in spectraldb and subcategory in spectraldb[category]:
                        material_def = spectraldb[category][subcategory]
                        material_name = material_def.split()[2]
                        if material_name not in written_materials:
                            file.write(material_def + "\n")
                            written_materials.add(material_name)
                        file.write(f"inherit alias {style_id} {material_name}\n")
                    else:
                        file.write(f"inherit alias {style_id} white\n")
                else:
                    # If the material is not mapped, alias it to white
                    file.write(f"inherit alias {style_id} white\n")

        self.report({"INFO"}, f"Exported Materials Rad file to: {materials_file}")

        # Run obj2mesh
        rtm_file_path = os.path.join(output_dir, "model.rtm")
        mesh_file_path = save_obj2mesh_output(obj_file_path, rtm_file_path, matfiles=[materials_file])
        # subprocess.run(["obj2mesh", "-a", materials_file, obj_file_path, rtm_file_path])
        self.report({"INFO"}, "obj2mesh output: {}".format(mesh_file_path))
        scene_file = os.path.join(output_dir, "scene.rad")
        with open(scene_file, "w") as file:
            file.write('void mesh model\n1 "' + rtm_file_path + '"\n0\n0\n')

        self.report({"INFO"}, "Exported Scene file to: {}".format(scene_file))

        print("Setting up Radiance scene...")
        scene = pr.Scene("ascene")

        material_path = os.path.join(output_dir, "materials.rad")
        scene_path = os.path.join(output_dir, "scene.rad")

        scene.add_material(material_path)
        scene.add_surface(scene_path)
        scene.add_source(sky_file_path)
        print("Setting up view...")
        if camera.data.type == "PERSP":
            # Perspective camera
            camera_fov = camera.data.angle
            # Calculate vertical FOV based on the desired aspect ratio
            vertical_fov = 2 * math.atan(math.tan(camera_fov / 2) / aspect_ratio)

            aview = pr.View(
                vtype="v",  # Perspective view
                position=camera_position,
                direction=camera_direction,
                vup=(0, 0, 1),  # Assuming Z is up
                horiz=math.degrees(camera_fov),
                vert=math.degrees(vertical_fov),
            )
        else:  # 'ORTHO'
            # Orthographic camera
            # Calculate the view size based on the camera's orthographic scale
            ortho_scale = camera.data.ortho_scale
            view_width = ortho_scale
            view_height = ortho_scale / aspect_ratio

            aview = pr.View(
                vtype="l",  # Parallel projection (orthographic)
                position=camera_position,
                direction=camera_direction,
                vup=(0, 0, 1),  # Assuming Z is up
                horiz=view_width,
                vert=view_height,
            )
        scene.add_view(aview)
        print("Starting render...")
        start_time = time.time()
        image = pr.render(
            scene,
            ambbounce=1,
            resolution=(resolution_x, resolution_y),
            quality=quality,
            detail=detail,
            variability=variability,
            nproc=multiprocessing.cpu_count(),
        )
        end_time = time.time()
        print(f"Render completed in {end_time - start_time:.2f} seconds")

        output_hdr_path = os.path.join(output_dir, f"{output_file_name}.{output_file_format.lower()}")
        print(f"Saving HDR output to: {output_hdr_path}")
        if output_file_format == "HDR":
            with open(output_hdr_path, "wb") as wtr:
                wtr.write(image)
        else:
            pass
        print("Applying tone mapping...")
        pcond_image = pr.pcond(hdr=output_hdr_path, human=True)

        tiff_path = os.path.join(output_dir, f"{output_file_name}.tiff")
        print(f"Saving TIFF output to: {tiff_path}")
        pr.ra_tiff(inp=pcond_image, out=tiff_path, lzw=True)
        print("Radiance rendering process completed successfully.")
        self.report({"INFO"}, "Radiance rendering completed. Output: {}".format(tiff_path))
        return {"FINISHED"}

    def get_active_camera(self, context):
        props = context.scene.radiance_exporter_properties
        if props.use_active_camera:
            return context.scene.camera
        else:
            return props.selected_camera

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

        props.materials.clear()

        for style in ifc_file.by_type("IfcSurfaceStyle"):
            for render_item in style.Styles:
                if render_item.is_a("IfcSurfaceStyleRendering"):
                    style_id = f"IfcSurfaceStyleRendering-{render_item.id()}"
                    style_name = style.Name or f"Unnamed Style {render_item.id()}"

                    # Extract color and transparency
                    color = (1.0, 1.0, 1.0)  # Default white
                    transparency = 0.0  # Default opaque
                    if render_item.SurfaceColour:
                        color = (
                            render_item.SurfaceColour.Red,
                            render_item.SurfaceColour.Green,
                            render_item.SurfaceColour.Blue,
                        )
                    if hasattr(render_item, "Transparency") and render_item.Transparency is not None:
                        transparency = render_item.Transparency

                    # Add material with color
                    material = props.add_material_mapping(style_id, style_name)
                    material.color = color

                    # If transparency is high, consider it as glass
                    if transparency > 0.5:
                        material.category = "Glass"
                        material.subcategory = "Clear Glass"
                        material.is_mapped = True

        props.active_material_index = 0 if props.materials else -1

        self.report({"INFO"}, f"Refreshed {len(props.materials)} IFC materials")
        return {"FINISHED"}


class UnmapMaterial(bpy.types.Operator):
    bl_idname = "bim.unmap_material"
    bl_label = "Unmap Material"
    bl_options = {"REGISTER", "UNDO"}

    material_index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.radiance_exporter_properties
        material = props.materials[self.material_index]
        props.unmap_material(material.name)
        return {"FINISHED"}


class RADIANCE_OT_select_camera(bpy.types.Operator):
    bl_idname = "radiance.select_camera"
    bl_label = "Select Camera"
    bl_description = "Select a camera from the viewport"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "CAMERA"

    def execute(self, context):
        props = context.scene.radiance_exporter_properties
        props.selected_camera = context.object
        props.use_active_camera = False
        return {"FINISHED"}


class RADIANCE_OT_export_material_mappings(bpy.types.Operator, ExportHelper):
    bl_idname = "radiance.export_material_mappings"
    bl_label = "Export Material Mappings"
    bl_description = "Export material mappings to a JSON file"

    filename_ext = ".json"

    def execute(self, context):
        props = context.scene.radiance_exporter_properties
        mappings = {}

        for material in props.materials:
            if material.is_mapped:
                mappings[material.style_id] = {
                    "name": material.name,
                    "category": material.category,
                    "subcategory": material.subcategory,
                }

        with open(self.filepath, "w") as f:
            json.dump(mappings, f, indent=4)

        self.report({"INFO"}, f"Material mappings exported to {self.filepath}")
        return {"FINISHED"}


class RADIANCE_OT_import_material_mappings(bpy.types.Operator, ImportHelper):
    bl_idname = "radiance.import_material_mappings"
    bl_label = "Import Material Mappings"
    bl_description = "Import material mappings from a JSON file"

    filename_ext = ".json"

    def execute(self, context):
        props = context.scene.radiance_exporter_properties
        props.import_mappings(self.filepath)
        self.report({"INFO"}, f"Material mappings imported from {self.filepath}")
        return {"FINISHED"}


class RADIANCE_OT_open_spectraldb(bpy.types.Operator):
    bl_idname = "radiance.open_spectraldb"
    bl_label = "Open SpectralDB"
    bl_description = "Open the SpectralDB website for reference"

    def execute(self, context):
        webbrowser.open("https://spectraldb.com")
        return {"FINISHED"}

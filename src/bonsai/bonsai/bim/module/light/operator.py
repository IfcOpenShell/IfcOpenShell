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

import pyradiance as pr
from datetime import datetime
import bpy
import bonsai.tool as tool
from pathlib import Path
from typing import Union, TYPE_CHECKING
import json
import math
import time
import ifcopenshell
import ifcopenshell.util.geolocation
import webbrowser
import ifcopenshell.geom
import multiprocessing
import requests
from math import radians
from mathutils import Vector
from bonsai.bim.module.light.data import SolarData
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper

ifc_materials = []

scene = None

with open(os.path.join(os.path.dirname(__file__), "spectraldb.json"), "r") as f:
    spectraldb = json.load(f)


class ExportOBJ(bpy.types.Operator):
    """Exports the IFC File to OBJ"""

    bl_idname = "export_scene.radiance"
    bl_label = "Export"
    bl_description = "Export the IFC to OBJ"

    @classmethod
    def poll(cls, context):
        props = tool.Blender.get_radiance_exporter_props()
        if not props.should_load_from_memory and not props.ifc_file:
            cls.poll_message_set("Select an IFC file or use 'load from memory' if it's loaded in Bonsai.")
            return False
        return True

    def execute(self, context):

        # Get the output directory
        props = tool.Blender.get_radiance_exporter_props()
        should_load_from_memory = props.should_load_from_memory
        output_dir = props.output_dir

        props.is_exporting = True

        # Conversion from IFC to OBJ
        # Settings for obj
        settings = ifcopenshell.geom.settings()
        serializer_settings = ifcopenshell.geom.serializer_settings()

        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.SURFACES_AND_SOLIDS)
        settings.set("apply-default-materials", True)
        serializer_settings.set("use-element-guids", True)
        settings.set("use-world-coords", True)

        ifc_file: ifcopenshell.file
        if should_load_from_memory:
            ifc_file = tool.Ifc.get()

        else:
            ifc_file_path = props.ifc_file
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
        props.is_exporting = False

        self.report({"INFO"}, "Exported OBJ file to: {}".format(obj_file_path))

        return {"FINISHED"}


class PrepareRadianceScene(bpy.types.Operator):
    bl_idname = "scene.prepare_radiance"
    bl_label = "Prepare Radiance Scene"
    bl_description = "Prepares the Radiance scene by creating necessary files and setting up the view"

    def get_camera_data(self, camera):
        # Get camera position
        position = camera.matrix_world.to_translation()

        # Get camera direction
        direction = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        direction.normalize()

        # Get camera up vector
        up = camera.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        up.normalize()

        # Ensure up vector is perpendicular to view direction
        # If they're parallel, use a different reference vector
        if abs(direction.dot(up)) > 0.99:  # Nearly parallel
            # Use world Y axis as reference, or X axis if that's also parallel
            if abs(direction.dot(Vector((0, 1, 0)))) > 0.99:
                reference = Vector((1, 0, 0))
            else:
                reference = Vector((0, 1, 0))
            # Compute perpendicular up vector using cross product
            right = direction.cross(reference)
            if right.length < 0.01:  # Still parallel, try another reference
                reference = Vector((0, 0, 1))
                right = direction.cross(reference)
            right.normalize()
            up = right.cross(direction)
            up.normalize()

        return (
            (position.x, position.y, position.z),
            (direction.x, direction.y, direction.z),
            (up.x, up.y, up.z),
        )

    def execute(self, context):
        print("Starting Radiance scene preparation...")
        props = tool.Blender.get_radiance_exporter_props()
        output_dir = props.output_dir

        # Check if OBJ file exists from previous export step
        obj_file_path = os.path.join(output_dir, "model.obj")
        if not os.path.exists(obj_file_path):
            error_msg = "OBJ file not found. Please run 'Export Geometry for Simulation' first."
            self.report({"ERROR"}, error_msg)
            print(f"ERROR: {error_msg}")
            print(f"  Expected file: {obj_file_path}")
            return {"CANCELLED"}

        resolution_x, resolution_y = props.radiance_resolution_x, props.radiance_resolution_y

        assert context.scene
        context.scene.render.resolution_x = resolution_x
        context.scene.render.resolution_y = resolution_y

        aspect_ratio = resolution_x / resolution_y

        quality = props.radiance_quality.upper()
        detail = props.radiance_detail.upper()
        variability = props.radiance_variability.upper()
        use_hdr = props.use_hdr
        choose_hdr_image = props.choose_hdr_image

        global scene
        scene = None

        print(f"Resolution: {resolution_x}x{resolution_y}")
        print(f"Quality: {quality}, Detail: {detail}, Variability: {variability}")
        print(f"Output directory: {output_dir}")
        print(f"Found OBJ file: {obj_file_path} ({os.path.getsize(obj_file_path)} bytes)")

        if use_hdr:
            hdr_image = "noon_grass_2k.hdr"
            hdr_mask = "noon_grass_2k_mask.hdr"
            sky_map_cal = "skymap.cal"
            hdr_image_path = os.path.join(os.path.dirname(__file__), "HDRs", hdr_image)
            hdr_mask_path = os.path.join(os.path.dirname(__file__), "HDRs", hdr_mask)
            sky_map_cal_path = os.path.join(os.path.dirname(__file__), "HDRs", sky_map_cal)

        sky_file_path = os.path.join(output_dir, "sky.rad")

        print("Setting up camera...")
        if props.use_active_camera:
            camera = context.scene.camera
        else:
            camera = props.selected_camera

        if camera is None:
            self.report({"ERROR"}, "No active camera found in the scene. Please add a camera and set it as active.")
            return {"CANCELLED"}

        # Get camera position, direction, and up vector
        camera_position, camera_direction, camera_up = self.get_camera_data(camera)

        print(f"Camera position: {camera_position}")
        print(f"Camera direction: {camera_direction}")
        print(f"Camera up: {camera_up}")

        # Generate sky file based on use_sun setting
        if props.use_sun:
            # Use sun position data to generate sky
            sun_props = tool.Blender.get_solar_props()
            sun_pos_props = tool.Blender.get_sun_props()
            if not sun_pos_props:
                self.report(
                    {"ERROR"}, "Sun position addon not available. Enable 'Sun Position' addon or disable 'Use Sun'."
                )
                return {"CANCELLED"}

            # Build datetime for Radiance gensky
            # Note: sun_pos_props and sun_props are synchronized by update_sun_path()
            dt = datetime(sun_pos_props.year, sun_props.month, sun_props.day, sun_props.hour, sun_props.minute)

            print(f"Sun position data for Radiance gensky:")
            print(f"  DateTime: {dt}")
            print(f"  Latitude: {sun_props.latitude}°")
            print(f"  Longitude: {sun_props.longitude}°")
            print(f"  UTC Zone: {sun_props.UTC_zone}")
            print(f"  Year: {sun_pos_props.year}")
            # Map sky condition enum to boolean parameters
            sky_condition = props.sky_condition
            sunny_with_sun = sky_condition == "SUNNY_WITH_SUN"
            sunny_without_sun = sky_condition == "SUNNY_WITHOUT_SUN"
            cloudy = sky_condition == "CLOUDY"

            sky_description = pr.gensky(
                dt=dt,
                latitude=sun_props.latitude,
                longitude=sun_props.longitude,
                year=sun_pos_props.year,
                timezone=-int(sun_props.UTC_zone),
                sunny_with_sun=sunny_with_sun,
                sunny_without_sun=sunny_without_sun,
                cloudy=cloudy,
                ground_reflectance=props.ground_reflectance,
                turbidity=props.turbidity,
            )

            sky_description_str = sky_description.decode("utf-8")
        else:
            # Skip sky generation when use_sun is False
            print("Skipping sky generation (use_sun is False)...")
            sky_description_str = None

        # Only generate sky.rad file when use_sun is True
        if props.use_sun:
            if use_hdr and choose_hdr_image == "Noon":
                with open(sky_file_path, "w") as f:
                    f.write(sky_description_str)
                    f.write("\n")
                    # When using sun, skyfunc is defined by gensky, so we can use it
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
                    # When using sun, skyfunc is defined by gensky
                    f.write("skyfunc glow sky_glow\n0\n0\n4 .9 .9 1.15 0\n")
                    f.write("sky_glow source sky\n0\n0\n4 0 0 1 180\n")
                    f.write("skyfunc glow ground_glow\n0\n0\n4 1.4 .9 .6 0\n")
                    f.write("ground_glow source ground\n0\n0\n4 0 0 -1 180\n")

        props = tool.Blender.get_radiance_exporter_props()

        # data = props.get_mappings_dict()

        materials_file = os.path.join(output_dir, "materials.rad")
        written_materials = set()

        all_materials = set(ifc_materials)

        with open(materials_file, "w") as file:
            # Write default materials
            default_materials = [
                "void plastic white\n0\n0\n5 0.8 0.8 0.8 0 0\n",
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

        # Convert IES light files to Radiance format
        print("Processing IES light files...")
        converted_ies_lights = {}  # {index: (rad_path, dat_path)}
        for idx, ies_light in enumerate(props.ies_lights):
            if not ies_light.is_enabled or not ies_light.ies_file_path or not ies_light.target_object:
                continue
            try:
                rad_file, dat_file = convert_ies_to_radiance(
                    ies_light.ies_file_path,
                    output_dir,
                    lamp_type=ies_light.lamp_type,
                    lamp_color=ies_light.lamp_color,
                    multiply_factor=ies_light.multiply_factor,
                    radius=ies_light.radius,
                )
                converted_ies_lights[idx] = (rad_file, dat_file)
                print(f"  Converted IES light {idx}: {Path(ies_light.ies_file_path).name}")
            except Exception as e:
                print(f"  ERROR converting IES light {idx}: {str(e)}")
                self.report({"WARNING"}, f"Failed to convert IES light: {str(e)}")

        print(f"OBJ file size: {os.path.getsize(obj_file_path)} bytes")
        print(f"Materials file size: {os.path.getsize(materials_file)} bytes")
        print(f"Converting OBJ to RTM format...")

        # Run obj2mesh
        rtm_file_path = os.path.join(output_dir, "model.rtm")
        try:
            mesh_file_path = save_obj2mesh_output(obj_file_path, rtm_file_path, matfiles=[materials_file])
            self.report({"INFO"}, "obj2mesh output: {}".format(mesh_file_path))
        except Exception as e:
            error_msg = f"Failed to convert OBJ to RTM: {str(e)}"
            self.report({"ERROR"}, error_msg)
            print(f"ERROR: {error_msg}")
            print(f"Check the console output above for more details")
            return {"CANCELLED"}
        scene_file = os.path.join(output_dir, "scene.rad")
        with open(scene_file, "w") as file:
            file.write('void mesh model\n1 "' + rtm_file_path + '"\n0\n0\n')
            file.write("\n")

            # Add IES light fixtures
            if len(props.ies_lights) > 0:
                file.write("\n# IES Light Fixtures\n")
                for idx, ies_light in enumerate(props.ies_lights):
                    if ies_light.ies_file_path and ies_light.target_object:
                        obj = ies_light.target_object
                        pos = obj.location
                        z_rot = ies_light.rotation_z

                        if idx in converted_ies_lights:
                            # Light is enabled and was converted
                            rad_path = converted_ies_lights[idx][0]
                            rad_filename = Path(rad_path).name
                            xform_line = f"!xform -rz {z_rot} -t {pos.x} {pos.y} {pos.z} {rad_filename}\n"
                            file.write(xform_line)
                        else:
                            # Light is disabled or not converted - write as comment
                            rad_base = Path(ies_light.ies_file_path).stem
                            rad_filename = f"{rad_base}.rad"
                            xform_line = f"# !xform -rz {z_rot} -t {pos.x} {pos.y} {pos.z} {rad_filename}\n"
                            file.write(xform_line)

        self.report({"INFO"}, "Exported Scene file to: {}".format(scene_file))

        # Validate that at least one light source will be available
        has_sky = props.use_sun
        has_ies_lights = len(converted_ies_lights) > 0

        if not has_sky and not has_ies_lights:
            error_msg = "ERROR: No light sources available. Please enable 'Use Sun' or add and map IES light fixtures."
            self.report({"ERROR"}, error_msg)
            print(error_msg)
            return {"CANCELLED"}

        print("Setting up Radiance scene...")
        scene = pr.Scene("ascene")

        material_path = os.path.join(output_dir, "materials.rad")
        scene_path = os.path.join(output_dir, "scene.rad")

        scene.add_material(material_path)
        scene.add_surface(scene_path)

        # Add light source(s)
        if props.use_sun:
            scene.add_source(sky_file_path)
            print(f"Added sky light source")

        if has_ies_lights:
            print(f"Added {len(converted_ies_lights)} IES light source(s)")
        print("Setting up view...")
        assert isinstance(camera.data, bpy.types.Camera)
        if camera.data.type == "PERSP":
            # Perspective camera
            camera_fov = camera.data.angle
            # Calculate vertical FOV based on the desired aspect ratio
            vertical_fov = 2 * math.atan(math.tan(camera_fov / 2) / aspect_ratio)

            aview = pr.create_default_view()
            aview.type = "v"  # Perspective view
            aview.vp = camera_position
            aview.vdir = camera_direction
            aview.vu = camera_up  # Use computed up vector perpendicular to view direction
            aview.horiz = math.degrees(camera_fov)
            aview.vert = math.degrees(vertical_fov)
        else:  # 'ORTHO'
            # Orthographic camera
            # Calculate the view size based on the camera's orthographic scale
            ortho_scale = camera.data.ortho_scale
            view_width = ortho_scale
            view_height = ortho_scale / aspect_ratio

            aview = pr.create_default_view()
            aview.type = "l"  # Parallel projection (orthographic)
            aview.vp = camera_position
            aview.vdir = camera_direction
            aview.vu = camera_up  # Use computed up vector perpendicular to view direction
            aview.horiz = view_width
            aview.vert = view_height
        scene.add_view(aview)
        print("Starting render...")

        self.report({"INFO"}, "Radiance scene prepared successfully.")
        return {"FINISHED"}


class RadianceRender(bpy.types.Operator):
    """Radiance Rendering"""

    bl_idname = "render_scene.radiance"
    bl_label = "Render"
    bl_description = "Renders the scene using Radiance"

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        resolution_x, resolution_y = props.radiance_resolution_x, props.radiance_resolution_y

        context.scene.render.resolution_x = resolution_x
        context.scene.render.resolution_y = resolution_y

        quality = props.radiance_quality.upper()
        detail = props.radiance_detail.upper()
        variability = props.radiance_variability.upper()
        output_dir = props.output_dir
        output_file_name = props.output_file_name
        output_file_format = props.output_file_format

        global scene

        start_time = time.time()
        cwd_saved = os.getcwd()
        os.chdir(output_dir)
        image = pr.render(
            scene,
            ambbounce=1,
            resolution=(resolution_x, resolution_y),
            quality=quality,
            detail=detail,
            variability=variability,
            nproc=multiprocessing.cpu_count(),
        )
        os.chdir(cwd_saved)
        end_time = time.time()
        print(f"Render completed in {end_time - start_time:.2f} seconds")

        output_hdr_path = os.path.join(output_dir, f"{output_file_name}.hdr")
        print(f"Saving HDR output to: {output_hdr_path}")
        with open(output_hdr_path, "wb") as wtr:
            wtr.write(image)

        if output_file_format == "HDR_TIFF":
            print("Applying tone mapping...")
            pcond_image = pr.pcond(hdr=output_hdr_path, human=True)

            tiff_path = os.path.join(output_dir, f"{output_file_name}.tiff")
            print(f"Saving TIFF output to: {tiff_path}")
            pr.ra_tiff(inp=pcond_image, out=tiff_path, lzw=True)

        print("Radiance rendering process completed successfully.")
        self.report({"INFO"}, f"Radiance rendering completed. HDR Output: {output_hdr_path}")
        if output_file_format == "HDR_TIFF":
            self.report({"INFO"}, f"TIFF Output: {tiff_path}")
        return {"FINISHED"}


class FalseColorRadiance(bpy.types.Operator):
    """Generate false color HDR image for illuminance analysis"""

    bl_idname = "render_scene.false_color_radiance"
    bl_label = "Generate False Color Image"
    bl_description = "Generate a false color HDR image for illuminance analysis"

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        output_dir = props.output_dir
        output_file_name = props.output_file_name

        # Check if the main render HDR exists
        hdr_path = os.path.join(output_dir, f"{output_file_name}.hdr")
        if not os.path.exists(hdr_path):
            error_msg = (
                f"HDR file not found at: {hdr_path}. Please run 'Radiance Render' first to generate the HDR output."
            )
            self.report({"ERROR"}, error_msg)
            print(f"ERROR: {error_msg}")
            return {"CANCELLED"}

        print(f"Generating false color image from: {hdr_path}")

        # Build false color parameters
        fc_scale = (
            str(int(props.false_color_scale))
            if props.false_color_scale == int(props.false_color_scale)
            else str(props.false_color_scale)
        )

        # Determine contour mode
        contour_mode = "l" if props.false_color_contour_lines else None

        # Get multiplier based on label selection
        if props.false_color_label == "fc":
            multiplier = props.false_color_multiplier  # Foot-candles default: 16.6295
        elif props.false_color_label == "lux":
            multiplier = props.false_color_multiplier if props.false_color_multiplier != 16.629505759940542 else 179.0
        else:  # cd/m2
            multiplier = props.false_color_multiplier if props.false_color_multiplier != 16.629505759940542 else 179.0

        print(f"False color parameters:")
        print(f"  Label: {props.false_color_label}")
        print(f"  Scale: {fc_scale}")
        print(f"  Contour lines: {props.false_color_contour_lines}")
        print(f"  Multiplier: {multiplier}")

        try:
            import subprocess

            # Build command line arguments for falsecolor
            # Format: falsecolor [options] -ip input.hdr > output.hdr
            fc_output_name = props.false_color_output_name
            fc_hdr_path = os.path.join(output_dir, f"{fc_output_name}.hdr")

            # Get path to bundled falsecolor executable
            light_module_dir = os.path.dirname(__file__)
            falsecolor_exe = os.path.join(light_module_dir, "Radiance", "bin", "falsecolor.exe")
            radiance_lib = os.path.join(light_module_dir, "Radiance", "lib")
            falsecolor_bin = falsecolor_exe if os.path.exists(falsecolor_exe) else "falsecolor"

            cmd = [falsecolor_bin]

            # Add multiplier
            cmd.extend(["-m", str(multiplier)])

            # Add scale
            cmd.extend(["-s", fc_scale])

            # Add label
            cmd.extend(["-l", props.false_color_label])

            # Add contour lines if enabled
            if props.false_color_contour_lines:
                cmd.append("-cl")

            # Add -ip flag (use same image for intensity and overlay)
            cmd.append("-ip")
            cmd.append(hdr_path)

            print(f"Running falsecolor command: {' '.join(cmd)}")
            print(f"Using falsecolor binary: {falsecolor_bin}")

            # Setup environment for Radiance tools
            env = os.environ.copy()
            env["RAYPATH"] = "." + os.pathsep + radiance_lib

            # Execute falsecolor and capture output
            try:
                result = subprocess.run(cmd, capture_output=True, check=True, env=env)
                fc_image = result.stdout

                print(f"Saving false color HDR to: {fc_hdr_path}")
                with open(fc_hdr_path, "wb") as f:
                    f.write(fc_image)

                print(f"False color HDR generated successfully: {fc_hdr_path}")
                self.report({"INFO"}, f"False color image generated: {fc_hdr_path}")

            except FileNotFoundError:
                # falsecolor binary not found in PATH or bundled location
                # Fallback: use pcond as an alternative visualization
                print("WARNING: falsecolor binary not found")
                print(f"  Checked locations:")
                print(f"    1. Bundled: {falsecolor_exe}")
                print(f"    2. System PATH: falsecolor")
                print("Using alternative method: Tone-mapped HDR for luminance visualization...")
                print("Note: This is a fallback visualization without false color overlay")

                fc_image = pr.pcond(hdr=hdr_path, human=True)

                # Still save as HDR for consistency
                with open(fc_hdr_path, "wb") as f:
                    f.write(fc_image)

                print(f"Tone-mapped HDR saved to: {fc_hdr_path}")
                self.report(
                    {"WARNING"},
                    "falsecolor binary not found. Generated tone-mapped HDR instead. "
                    "Ensure Radiance/bin folder is present in the light module directory.",
                )

            except subprocess.CalledProcessError as e:
                error_msg = f"falsecolor failed: {e.stderr.decode() if e.stderr else str(e)}"
                print(f"ERROR: {error_msg}")
                raise RuntimeError(error_msg)

            # Generate TIFF version for convenience
            try:
                print("Generating TIFF version of false color image...")
                pcond_fc_image = pr.pcond(hdr=fc_hdr_path, human=True)
                fc_tiff_path = os.path.join(output_dir, f"{fc_output_name}.tiff")
                print(f"Saving false color TIFF to: {fc_tiff_path}")
                pr.ra_tiff(inp=pcond_fc_image, out=fc_tiff_path, lzw=True)
                print(f"False color TIFF generated successfully: {fc_tiff_path}")
                self.report({"INFO"}, f"False color TIFF also generated: {fc_tiff_path}")
            except Exception as e:
                print(f"Warning: Failed to generate false color TIFF: {str(e)}")
                self.report({"WARNING"}, f"TIFF generation failed: {str(e)}")

            return {"FINISHED"}

        except Exception as e:
            error_msg = f"Failed to generate false color image: {str(e)}"
            self.report({"ERROR"}, error_msg)
            print(f"ERROR: {error_msg}")
            print(f"Traceback:")
            import traceback

            traceback.print_exc()
            return {"CANCELLED"}


class ConvertHDRToFootCandles(bpy.types.Operator):
    """Convert HDR image to foot-candles unit"""

    bl_idname = "render_scene.convert_hdr_to_fc"
    bl_label = "Convert HDR to Foot-Candles"
    bl_description = "Convert the main render HDR to foot-candles unit for illuminance verification"

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        output_dir = props.output_dir
        output_file_name = props.output_file_name

        # Check if the main render HDR exists
        hdr_path = os.path.join(output_dir, f"{output_file_name}.hdr")
        if not os.path.exists(hdr_path):
            error_msg = f"HDR file not found at: {hdr_path}. Please run 'Radiance Render' first."
            self.report({"ERROR"}, error_msg)
            print(f"ERROR: {error_msg}")
            return {"CANCELLED"}

        print(f"Converting HDR to foot-candles: {hdr_path}")

        # Conversion factor from cd/m² to foot-candles
        # 1 foot-candle = 10.764 lux = 10.764 cd/m²
        # So to convert: multiply by 1/10.764 ≈ 0.0929
        fc_scale_factor = 0.0929005

        try:
            # Use pyradiance Pcomb to convert
            print(f"Applying pcomb with scale factor {fc_scale_factor} and original flag...")

            # Create Pcomb command with original=True (-o flag) and scaler for unit conversion
            # Note: fout=False ensures the output is a proper HDR file with headers, not raw data
            pcomb_result = pr.Pcomb(fout=False).add(hdr_path, original=True, scaler=fc_scale_factor)()

            # Save the converted HDR
            fc_output_name = props.hdr_to_fc_output_name
            fc_hdr_path = os.path.join(output_dir, f"{fc_output_name}.hdr")

            print(f"Saving foot-candles HDR to: {fc_hdr_path}")
            with open(fc_hdr_path, "wb") as f:
                f.write(pcomb_result)

            print(f"HDR converted to foot-candles successfully: {fc_hdr_path}")
            self.report({"INFO"}, f"HDR converted to foot-candles: {fc_hdr_path}")

            # Also generate TIFF version for convenient viewing
            try:
                print("Generating TIFF version of foot-candles image...")
                pcond_fc_image = pr.pcond(hdr=fc_hdr_path, human=True)
                fc_tiff_path = os.path.join(output_dir, f"{fc_output_name}.tiff")
                print(f"Saving foot-candles TIFF to: {fc_tiff_path}")
                pr.ra_tiff(inp=pcond_fc_image, out=fc_tiff_path, lzw=True)
                print(f"TIFF version generated: {fc_tiff_path}")
                self.report({"INFO"}, f"TIFF version also generated: {fc_tiff_path}")
            except Exception as e:
                print(f"Warning: Failed to generate foot-candles TIFF: {str(e)}")
                self.report({"WARNING"}, f"TIFF generation failed: {str(e)}")

            print("Foot-candles conversion completed successfully.")
            return {"FINISHED"}

        except Exception as e:
            error_msg = f"Failed to convert HDR to foot-candles: {str(e)}"
            self.report({"ERROR"}, error_msg)
            print(f"ERROR: {error_msg}")
            print(f"Traceback:")
            import traceback

            traceback.print_exc()
            return {"CANCELLED"}


def save_obj2mesh_output(inp: Union[bytes, str, Path], output_file: str, **kwargs):
    try:
        output_bytes = pr.obj2mesh(inp, **kwargs)
        with open(output_file, "wb") as f:
            f.write(output_bytes)
        return output_file
    except Exception as e:
        print(f"ERROR in obj2mesh conversion:")
        print(f"  Input file: {inp}")
        print(f"  Output file: {output_file}")
        print(f"  Additional args: {kwargs}")
        print(f"  Error: {str(e)}")
        raise


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


class RefreshIFCMaterials(bpy.types.Operator):
    bl_idname = "bim.refresh_ifc_materials"
    bl_label = "Refresh IFC Materials"
    bl_description = "Refresh the list of IFC materials for mapping"

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        ifc_file: ifcopenshell.file
        ifc_file = tool.Ifc.get() if props.should_load_from_memory else ifcopenshell.open(props.ifc_file)

        props.materials.clear()

        for style in ifc_file.by_type("IfcSurfaceStyle"):
            for render_item in style.Styles:
                if render_item.is_a("IfcSurfaceStyleRendering"):
                    style_id = f"IfcSurfaceStyleRendering-{render_item.id()}"
                    style_name = style.Name or f"Unnamed Style {render_item.id()}"

                    # Extract color
                    color = (1.0, 1.0, 1.0)  # Default white
                    if render_item.SurfaceColour:
                        color = (
                            render_item.SurfaceColour.Red,
                            render_item.SurfaceColour.Green,
                            render_item.SurfaceColour.Blue,
                        )

                    material = props.add_material_mapping(style_id, style_name)
                    material.color = color

                    material.category = ""
                    material.subcategory = ""
                    material.is_mapped = False

        props.active_material_index = 0 if props.materials else -1

        self.report({"INFO"}, f"Refreshed {len(props.materials)} IFC materials")
        return {"FINISHED"}


class UnmapMaterial(bpy.types.Operator):
    bl_idname = "bim.unmap_material"
    bl_label = "Unmap Material"
    bl_options = {"REGISTER", "UNDO"}

    material_index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
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
        props = tool.Blender.get_radiance_exporter_props()
        props.selected_camera = context.object
        props.use_active_camera = False
        return {"FINISHED"}


class RADIANCE_OT_export_material_mappings(bpy.types.Operator, ExportHelper):
    bl_idname = "radiance.export_material_mappings"
    bl_label = "Export Material Mappings"
    bl_description = "Export material mappings to a JSON file"

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
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
        props = tool.Blender.get_radiance_exporter_props()
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


class EnumPropertySearch(bpy.types.Operator):
    bl_idname = "bim.enum_property_search"
    bl_label = "Search Enum Property"
    bl_options = {"REGISTER", "UNDO"}

    prop_name: bpy.props.StringProperty()
    search_term: bpy.props.StringProperty()

    def execute(self, context):
        data = context.space_data.context_pointer_get("data")
        enum_items = get_enum_items(data, self.prop_name)
        filtered_items = [item for item in enum_items if self.search_term.lower() in item[1].lower()]

        def draw_menu(self, context):
            layout = self.layout
            for item in filtered_items:
                props = layout.operator("bim.set_enum_property", text=item[1])
                props.prop_name = self.prop_name
                props.enum_value = item[0]

        bpy.context.window_manager.popup_menu(draw_menu, title="Search Results", icon="VIEWZOOM")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "search_term", text="Search")


class SetEnumProperty(bpy.types.Operator):
    bl_idname = "bim.set_enum_property"
    bl_label = "Set Enum Property"
    bl_options = {"REGISTER", "UNDO"}

    prop_name: bpy.props.StringProperty()
    enum_value: bpy.props.StringProperty()

    def execute(self, context):
        data = context.space_data.context_pointer_get("data")
        setattr(data, self.prop_name, self.enum_value)
        return {"FINISHED"}


def convert_ies_to_radiance(
    ies_file_path: str,
    output_dir: str,
    lamp_type: str = "",
    lamp_color: tuple[float, float, float] = (1.0, 1.0, 1.0),
    multiply_factor: float = 1.0,
    radius: float = 0.0,
) -> tuple[str, str]:
    """
    Convert IES file to Radiance format using pyradiance.

    Args:
        ies_file_path: Path to the .ies file
        output_dir: Directory where .rad and .dat files will be saved
        lamp_type: Type of lamp (e.g., 'LED', 'metal halide')
        lamp_color: RGB color tuple (0.0-1.0 each)
        multiply_factor: Brightness multiplier (0.1-10.0)
        radius: Illum sphere radius (0 = use IES geometry)

    Returns:
        Tuple of (rad_file_path, dat_file_path)
    """
    try:
        import pyradiance as pr

        ies_path = Path(ies_file_path)
        base_name = ies_path.stem

        # ies2rad creates .rad and .dat files
        # We pass the output name root (without extension)
        output_path = os.path.join(output_dir, base_name)

        # Build ies2rad parameters
        kwargs = {"outname": output_path}

        if lamp_type:
            kwargs["lamp_type"] = lamp_type

        if lamp_color != (1.0, 1.0, 1.0):
            kwargs["lamp_color"] = lamp_color

        if multiply_factor != 1.0:
            kwargs["multiply_factor"] = multiply_factor

        if radius > 0.0:
            kwargs["radius"] = radius

        # Call ies2rad to convert the file
        pr.ies2rad(ies_path, **kwargs)

        rad_file = os.path.join(output_dir, f"{base_name}.rad")
        dat_file = os.path.join(output_dir, f"{base_name}.dat")

        return rad_file, dat_file

    except Exception as e:
        raise RuntimeError(f"Failed to convert IES file '{ies_file_path}': {str(e)}")


class AddIESLight(bpy.types.Operator, ImportHelper):
    """Upload and add an IES light fixture to the scene"""

    bl_idname = "radiance.add_ies_light"
    bl_label = "Add IES Light"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".ies"
    filter_glob: bpy.props.StringProperty(default="*.ies;*.IES", options={"HIDDEN"})

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()

        # Create new IES light entry
        ies_light = props.ies_lights.add()
        ies_light.ies_file_path = self.filepath
        ies_light.rotation_z = 0.0
        ies_light.is_enabled = True

        # Set as active
        props.active_ies_light_index = len(props.ies_lights) - 1

        self.report({"INFO"}, f"Added IES light: {Path(self.filepath).name}")
        return {"FINISHED"}


class RemoveIESLight(bpy.types.Operator):
    """Remove an IES light fixture mapping"""

    bl_idname = "radiance.remove_ies_light"
    bl_label = "Remove IES Light"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()

        if 0 <= self.index < len(props.ies_lights):
            props.ies_lights.remove(self.index)

            # Adjust active index if needed
            if props.active_ies_light_index >= len(props.ies_lights):
                props.active_ies_light_index = len(props.ies_lights) - 1

            self.report({"INFO"}, "IES light removed")
            return {"FINISHED"}

        self.report({"WARNING"}, "Invalid IES light index")
        return {"CANCELLED"}


class SetIESLightObject(bpy.types.Operator):
    """Set the target Empty object for an IES light via eyedropper"""

    bl_idname = "radiance.set_ies_light_object"
    bl_label = "Set IES Light Object"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(description="Index of IES light to set object for")

    def execute(self, context):
        if context.object is None or context.object.type != "EMPTY":
            self.report({"WARNING"}, "Please select an Empty object")
            return {"CANCELLED"}

        props = tool.Blender.get_radiance_exporter_props()

        if 0 <= self.index < len(props.ies_lights):
            ies_light = props.ies_lights[self.index]
            ies_light.target_object = context.object
            props.active_ies_light_index = self.index
            self.report({"INFO"}, f"Set target object to: {context.object.name}")
            return {"FINISHED"}

        self.report({"WARNING"}, "Invalid IES light index")
        return {"CANCELLED"}

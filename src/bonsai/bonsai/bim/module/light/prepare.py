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

import math
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Union

import bpy
import pyradiance as pr
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.light.prop import spectraldb
from bonsai.bim.module.light.shared import ifc_materials, linked_model_exports


def _matrix_to_xform_args(matrix: list[list[float]]) -> str:
    """Decompose a 4x4 matrix into Radiance xform arguments.

    Decomposes into Z/Y/X Euler rotations + translation.
    The matrix is expected in row-major format (Blender convention).
    xform applies transforms right-to-left, so we write: -rx X -ry Y -rz Z -t tx ty tz
    """
    from mathutils import Matrix as MMatrix

    m = MMatrix(matrix)
    translation = m.to_translation()
    euler = m.to_euler("XYZ")

    parts = []
    rx = math.degrees(euler.x)
    ry = math.degrees(euler.y)
    rz = math.degrees(euler.z)

    if abs(rx) > 1e-6:
        parts.append(f"-rx {rx:.6f}")
    if abs(ry) > 1e-6:
        parts.append(f"-ry {ry:.6f}")
    if abs(rz) > 1e-6:
        parts.append(f"-rz {rz:.6f}")

    parts.append(f"-t {translation.x:.6f} {translation.y:.6f} {translation.z:.6f}")

    return " ".join(parts)


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


def convert_ies_to_radiance(
    ies_file_path: str,
    output_dir: str,
    lamp_type: str = "",
    lamp_color: tuple[float, float, float] = (1.0, 1.0, 1.0),
    multiply_factor: float = 1.0,
    radius: float = 0.0,
) -> tuple[str, str]:
    """Convert IES file to Radiance format using pyradiance.

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
        ies_path = Path(bpy.path.abspath(ies_file_path))
        base_name = ies_path.stem

        output_path = os.path.join(output_dir, base_name)

        kwargs = {"outname": output_path}

        if lamp_type:
            kwargs["lamp_type"] = lamp_type

        if lamp_color != (1.0, 1.0, 1.0):
            kwargs["lamp_color"] = lamp_color

        if multiply_factor != 1.0:
            kwargs["multiply_factor"] = multiply_factor

        if radius > 0.0:
            kwargs["radius"] = radius

        pr.ies2rad(ies_path, **kwargs)

        rad_file = os.path.join(output_dir, f"{base_name}.rad")
        dat_file = os.path.join(output_dir, f"{base_name}.dat")

        return rad_file, dat_file

    except Exception as e:
        raise RuntimeError(f"Failed to convert IES file '{ies_file_path}': {str(e)}")


class PrepareRadianceScene(bpy.types.Operator):
    """Prepares the Radiance scene (runs heavy work in background thread)"""

    bl_idname = "scene.prepare_radiance"
    bl_label = "Prepare Radiance Scene"
    bl_description = "Prepares the Radiance scene by creating necessary files and setting up the view"

    _timer = None
    _thread: Union[threading.Thread, None] = None
    _error: Union[str, None] = None
    _start_time: float = 0.0

    @classmethod
    def poll(cls, context):
        props = tool.Blender.get_radiance_exporter_props()
        if not props.output_dir:
            cls.poll_message_set("Output directory is not set.")
            return False
        if props.is_preparing:
            cls.poll_message_set("Scene preparation is already in progress.")
            return False
        return True

    def get_camera_data(self, camera):
        position = camera.matrix_world.to_translation()

        direction = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        direction.normalize()

        up = camera.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        up.normalize()

        if abs(direction.dot(up)) > 0.99:
            if abs(direction.dot(Vector((0, 1, 0)))) > 0.99:
                reference = Vector((1, 0, 0))
            else:
                reference = Vector((0, 1, 0))
            right = direction.cross(reference)
            if right.length < 0.01:
                reference = Vector((0, 0, 1))
                right = direction.cross(reference)
            right.normalize()
            up = right.cross(direction)
            up.normalize()

        if up.length < 0.01:
            up = Vector((0, 0, 1))
        else:
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
        use_hdr = props.use_hdr
        choose_hdr_image = props.choose_hdr_image

        print(f"Resolution: {resolution_x}x{resolution_y}")
        print(f"Output directory: {output_dir}")
        print(f"Found OBJ file: {obj_file_path} ({os.path.getsize(obj_file_path)} bytes)")

        hdr_image_path = ""
        hdr_mask_path = ""
        sky_map_cal_path = ""
        if use_hdr:
            hdr_image_path = os.path.join(os.path.dirname(__file__), "HDRs", "noon_grass_2k.hdr")
            hdr_mask_path = os.path.join(os.path.dirname(__file__), "HDRs", "noon_grass_2k_mask.hdr")
            sky_map_cal_path = os.path.join(os.path.dirname(__file__), "HDRs", "skymap.cal")

        sky_file_path = os.path.join(output_dir, "sky.rad")

        print("Setting up camera...")
        if props.use_active_camera:
            camera = context.scene.camera
        else:
            camera = props.selected_camera

        if camera is None:
            self.report({"ERROR"}, "No active camera found in the scene. Please add a camera and set it as active.")
            return {"CANCELLED"}

        camera_position, camera_direction, camera_up = self.get_camera_data(camera)
        camera_type = camera.data.type
        camera_fov = camera.data.angle if camera_type == "PERSP" else 0.0
        camera_ortho_scale = camera.data.ortho_scale if camera_type == "ORTHO" else 0.0

        print(f"Camera position: {camera_position}")
        print(f"Camera direction: {camera_direction}")
        print(f"Camera up: {camera_up}")

        # Collect sky generation data (must be on main thread)
        sky_data = None
        if props.use_sun:
            sun_props = tool.Blender.get_solar_props()
            sun_pos_props = tool.Blender.get_sun_props()
            if not sun_pos_props:
                self.report(
                    {"ERROR"}, "Sun position addon not available. Enable 'Sun Position' addon or disable 'Use Sun'."
                )
                return {"CANCELLED"}

            sky_data = {
                "year": sun_props.year,
                "month": sun_props.month,
                "day": sun_props.day,
                "hour": sun_props.hour,
                "minute": sun_props.minute,
                "latitude": sun_props.latitude,
                "longitude": sun_props.longitude,
                "UTC_zone": sun_props.UTC_zone,
                "sun_year": sun_pos_props.year,
                "sky_condition": props.sky_condition,
                "ground_reflectance": props.ground_reflectance,
                "turbidity": props.turbidity,
            }

        # Collect IES light data (must be on main thread)
        ies_light_data = []
        for idx, ies_light in enumerate(props.ies_lights):
            if not ies_light.is_enabled or not ies_light.ies_file_path:
                ies_light_data.append(None)
                continue

            target_empties = ies_light.get_target_empties()
            if not target_empties:
                ies_light_data.append(None)
                continue

            positions = []
            for obj in target_empties:
                try:
                    positions.append((obj.location.x, obj.location.y, obj.location.z))
                except ReferenceError:
                    continue

            if not positions:
                ies_light_data.append(None)
                continue

            ies_light_data.append(
                {
                    "ies_file_path": ies_light.ies_file_path,
                    "lamp_type": ies_light.lamp_type,
                    "lamp_color": ies_light.lamp_color,
                    "multiply_factor": ies_light.multiply_factor,
                    "radius": ies_light.radius,
                    "rotation_z": ies_light.rotation_z,
                    "positions": positions,
                    "is_enabled": ies_light.is_enabled,
                }
            )

        # Collect material mapping data (must be on main thread)
        material_mappings = []
        for m in props.materials:
            material_mappings.append(
                {
                    "style_id": m.style_id,
                    "is_mapped": m.is_mapped,
                    "category": m.category,
                    "subcategory": m.subcategory,
                }
            )

        linked_exports_snapshot = list(linked_model_exports)

        # All Blender data collected — now launch background thread
        props.is_preparing = True
        self._start_time = time.time()
        self._error = None

        import bonsai.bim.module.light.shared as shared

        shared.scene = None

        self._thread = threading.Thread(
            target=self._prepare_worker,
            args=(
                output_dir,
                obj_file_path,
                sky_file_path,
                use_hdr,
                choose_hdr_image,
                hdr_image_path,
                hdr_mask_path,
                sky_map_cal_path,
                sky_data,
                ies_light_data,
                material_mappings,
                linked_exports_snapshot,
                camera_position,
                camera_direction,
                camera_up,
                camera_type,
                camera_fov,
                camera_ortho_scale,
                aspect_ratio,
            ),
            daemon=True,
        )
        self._thread.start()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        self.report({"INFO"}, "Scene preparation started in background...")
        context.window.cursor_set("WAIT")
        return {"RUNNING_MODAL"}

    def _prepare_worker(
        self,
        output_dir,
        obj_file_path,
        sky_file_path,
        use_hdr,
        choose_hdr_image,
        hdr_image_path,
        hdr_mask_path,
        sky_map_cal_path,
        sky_data,
        ies_light_data,
        material_mappings,
        linked_exports_snapshot,
        camera_position,
        camera_direction,
        camera_up,
        camera_type,
        camera_fov,
        camera_ortho_scale,
        aspect_ratio,
    ):
        """Runs in a background thread — no Blender API calls allowed here."""
        try:
            self._do_prepare(
                output_dir,
                obj_file_path,
                sky_file_path,
                use_hdr,
                choose_hdr_image,
                hdr_image_path,
                hdr_mask_path,
                sky_map_cal_path,
                sky_data,
                ies_light_data,
                material_mappings,
                linked_exports_snapshot,
                camera_position,
                camera_direction,
                camera_up,
                camera_type,
                camera_fov,
                camera_ortho_scale,
                aspect_ratio,
            )
        except Exception as e:
            self._error = str(e)
            import traceback

            traceback.print_exc()

    def _do_prepare(
        self,
        output_dir,
        obj_file_path,
        sky_file_path,
        use_hdr,
        choose_hdr_image,
        hdr_image_path,
        hdr_mask_path,
        sky_map_cal_path,
        sky_data,
        ies_light_data,
        material_mappings,
        linked_exports_snapshot,
        camera_position,
        camera_direction,
        camera_up,
        camera_type,
        camera_fov,
        camera_ortho_scale,
        aspect_ratio,
    ):
        """The actual preparation logic (no Blender API)."""
        import bonsai.bim.module.light.shared as shared

        # --- Generate sky file ---
        if sky_data is not None:
            dt = datetime(sky_data["year"], sky_data["month"], sky_data["day"], sky_data["hour"], sky_data["minute"])

            print(f"Sun position data for Radiance gensky:")
            print(f"  DateTime: {dt}")
            print(f"  Latitude: {sky_data['latitude']}°")
            print(f"  Longitude: {sky_data['longitude']}°")

            sky_condition = sky_data["sky_condition"]
            longitude_for_gensky = -sky_data["longitude"]
            timezone_for_gensky = -int(sky_data["UTC_zone"]) * 15

            sky_description = pr.gensky(
                dt=dt,
                latitude=sky_data["latitude"],
                longitude=longitude_for_gensky,
                year=sky_data["sun_year"],
                timezone=timezone_for_gensky,
                sunny_with_sun=sky_condition == "SUNNY_WITH_SUN",
                sunny_without_sun=sky_condition == "SUNNY_WITHOUT_SUN",
                cloudy=sky_condition == "CLOUDY",
                ground_reflectance=sky_data["ground_reflectance"],
                turbidity=sky_data["turbidity"],
            )

            sky_description_str = sky_description.decode("utf-8")

            if use_hdr and choose_hdr_image == "Noon":
                with open(sky_file_path, "w") as f:
                    f.write(sky_description_str)
                    f.write("\n")
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
                    f.write("skyfunc glow sky_glow\n0\n0\n4 .9 .9 1.15 0\n")
                    f.write("sky_glow source sky\n0\n0\n4 0 0 1 180\n")
                    f.write("skyfunc glow ground_glow\n0\n0\n4 1.4 .9 .6 0\n")
                    f.write("ground_glow source ground\n0\n0\n4 0 0 -1 180\n")
        else:
            print("Skipping sky generation (use_sun is False)...")

        # --- Write materials.rad ---
        materials_file = os.path.join(output_dir, "materials.rad")
        written_materials = set()

        all_materials = set(ifc_materials)

        with open(materials_file, "w") as file:
            default_materials = [
                "void plastic white\n0\n0\n5 0.8 0.8 0.8 0 0\n",
            ]
            for material in default_materials:
                file.write(material)
                written_materials.add(material.split()[2])

            for style_id in all_materials:
                mat_data = next((m for m in material_mappings if m["style_id"] == style_id), None)
                if mat_data and mat_data["is_mapped"]:
                    category, subcategory = mat_data["category"], mat_data["subcategory"]
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
                    file.write(f"inherit alias {style_id} white\n")

        print(f"Exported Materials Rad file to: {materials_file}")

        # --- Convert IES light files ---
        print("Processing IES light files...")
        converted_ies_lights = {}
        for idx, ies_data in enumerate(ies_light_data):
            if ies_data is None:
                continue
            try:
                rad_file, dat_file = convert_ies_to_radiance(
                    ies_data["ies_file_path"],
                    output_dir,
                    lamp_type=ies_data["lamp_type"],
                    lamp_color=ies_data["lamp_color"],
                    multiply_factor=ies_data["multiply_factor"],
                    radius=ies_data["radius"],
                )
                converted_ies_lights[idx] = (rad_file, dat_file)
                print(f"  Converted IES light {idx}: {Path(ies_data['ies_file_path']).name}")
            except Exception as e:
                print(f"  ERROR converting IES light {idx}: {str(e)}")

        # --- Convert OBJ to RTM ---
        print(f"OBJ file size: {os.path.getsize(obj_file_path)} bytes")
        print(f"Materials file size: {os.path.getsize(materials_file)} bytes")
        print(f"Converting OBJ to RTM format...")

        rtm_file_path = os.path.join(output_dir, "model.rtm")
        mesh_file_path = save_obj2mesh_output(obj_file_path, rtm_file_path, matfiles=[materials_file])
        print(f"obj2mesh output: {mesh_file_path}")

        # Convert linked model OBJs to RTM
        linked_rtm_files = []
        for link_idx, (link_obj_path, link_mtl_path, link_matrix) in enumerate(linked_exports_snapshot):
            if not os.path.exists(link_obj_path):
                print(f"Linked model OBJ not found: {link_obj_path}")
                continue
            link_rtm_path = os.path.join(output_dir, f"linked_{link_idx}.rtm")
            try:
                save_obj2mesh_output(link_obj_path, link_rtm_path, matfiles=[materials_file])
                linked_rtm_files.append((link_rtm_path, link_matrix))
                print(f"Converted linked model {link_idx} to RTM")
            except Exception as e:
                print(f"Failed to convert linked model {link_idx} to RTM: {e}")

        # --- Write scene.rad ---
        scene_file = os.path.join(output_dir, "scene.rad")
        with open(scene_file, "w") as file:
            file.write('void mesh model\n1 "' + rtm_file_path + '"\n0\n0\n')
            file.write("\n")

            if linked_rtm_files:
                file.write("\n# Linked Models\n")
                for link_idx, (link_rtm_path, link_matrix) in enumerate(linked_rtm_files):
                    is_identity = all(
                        abs(link_matrix[i][j] - (1.0 if i == j else 0.0)) < 1e-6 for i in range(4) for j in range(4)
                    )

                    if is_identity:
                        file.write(f'void mesh linked_{link_idx}\n1 "{link_rtm_path}"\n0\n0\n\n')
                        print(f"Added linked model {link_idx} to scene (identity, inline mesh)")
                    else:
                        link_rad_path = os.path.join(output_dir, f"linked_{link_idx}.rad")
                        with open(link_rad_path, "w") as link_file:
                            link_file.write(f'void mesh linked_{link_idx}\n1 "{link_rtm_path}"\n0\n0\n')

                        xform_args = _matrix_to_xform_args(link_matrix)
                        file.write(f'!xform {xform_args} "{link_rad_path}"\n')
                        print(f"Added linked model {link_idx} to scene with xform: {xform_args}")

            # IES light fixtures
            if ies_light_data:
                file.write("\n# IES Light Fixtures\n")
                for idx, ies_data in enumerate(ies_light_data):
                    if ies_data is None:
                        continue
                    z_rot = math.degrees(ies_data["rotation_z"])

                    for pos in ies_data["positions"]:
                        if idx in converted_ies_lights:
                            rad_path = converted_ies_lights[idx][0]
                            rad_filename = Path(rad_path).name
                            file.write(f'!xform -rz {z_rot} -t {pos[0]} {pos[1]} {pos[2]} "{rad_filename}"\n')
                        else:
                            rad_base = Path(ies_data["ies_file_path"]).stem
                            rad_filename = f"{rad_base}.rad"
                            file.write(f'# !xform -rz {z_rot} -t {pos[0]} {pos[1]} {pos[2]} "{rad_filename}"\n')

        print(f"Exported Scene file to: {scene_file}")

        # --- Validate light sources ---
        has_sky = sky_data is not None
        has_ies_lights = len(converted_ies_lights) > 0

        if not has_sky and not has_ies_lights:
            raise RuntimeError("No light sources available. Please enable 'Use Sun' or add and map IES light fixtures.")

        # --- Build pr.Scene ---
        print("Setting up Radiance scene...")
        new_scene = pr.Scene("ascene")

        material_path = os.path.join(output_dir, "materials.rad")
        scene_path = os.path.join(output_dir, "scene.rad")

        new_scene.add_material(material_path)
        new_scene.add_surface(scene_path)

        if has_sky:
            new_scene.add_source(sky_file_path)
            print(f"Added sky light source")

        if has_ies_lights:
            print(f"Added {len(converted_ies_lights)} IES light source(s)")

        print("Setting up view...")
        if camera_type == "PERSP":
            vertical_fov = 2 * math.atan(math.tan(camera_fov / 2) / aspect_ratio)
            aview = pr.create_default_view()
            aview.type = "v"
            aview.vp = camera_position
            aview.vdir = camera_direction
            aview.vu = camera_up
            aview.horiz = math.degrees(camera_fov)
            aview.vert = math.degrees(vertical_fov)
        else:
            view_width = camera_ortho_scale
            view_height = camera_ortho_scale / aspect_ratio
            aview = pr.create_default_view()
            aview.type = "l"
            aview.vp = camera_position
            aview.vdir = camera_direction
            aview.vu = camera_up
            aview.horiz = view_width
            aview.vert = view_height

        new_scene.add_view(aview)

        # Set the global scene reference (thread-safe assignment)
        shared.scene = new_scene
        print("Scene preparation complete.")

    def modal(self, context, event):
        if event.type == "TIMER":
            if self._thread is not None and self._thread.is_alive():
                return {"RUNNING_MODAL"}

            # Thread finished — clean up
            self._cleanup_timer(context)
            props = tool.Blender.get_radiance_exporter_props()
            props.is_preparing = False
            context.window.cursor_set("DEFAULT")

            if self._error:
                self.report({"ERROR"}, f"Scene preparation failed: {self._error}")
                return {"CANCELLED"}

            elapsed = time.time() - self._start_time
            self.report({"INFO"}, f"Radiance scene prepared successfully in {elapsed:.1f}s")
            print(f"Scene preparation completed in {elapsed:.2f} seconds")
            return {"FINISHED"}

        elif event.type == "ESC":
            self._cleanup_timer(context)
            props = tool.Blender.get_radiance_exporter_props()
            props.is_preparing = False
            context.window.cursor_set("DEFAULT")
            self.report({"WARNING"}, "Scene preparation cannot be cancelled mid-operation")
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def _cleanup_timer(self, context):
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None

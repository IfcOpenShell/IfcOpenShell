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

import json
import math
import multiprocessing
import os
import subprocess
import threading
import time
import webbrowser
from datetime import datetime
from math import radians
from pathlib import Path
from typing import TYPE_CHECKING, Union

import bpy
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.geolocation
import pyradiance as pr
import requests
from bpy_extras.io_utils import ExportHelper, ImportHelper
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.light.data import SolarData
from bonsai.bim.module.light.prop import spectraldb

ifc_materials = []

scene = None

# Stores info about exported linked models: list of (obj_path, mtl_path, link_matrix_4x4)
linked_model_exports: list[tuple[str, str, list[list[float]]]] = []


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

    def _get_geom_settings(self):
        """Create standard geometry and serializer settings for OBJ export."""
        settings = ifcopenshell.geom.settings()
        serializer_settings = ifcopenshell.geom.serializer_settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.SURFACES_AND_SOLIDS)
        settings.set("apply-default-materials", True)
        serializer_settings.set("use-element-guids", True)
        settings.set("use-world-coords", True)
        return settings, serializer_settings

    def _get_exportable_elements(self, ifc_file, filter_visibility=True):
        """Get the list of elements to export from an IFC file."""
        if ifc_file.schema in ("IFC2X3", "IFC4"):
            elements = ifc_file.by_type("IfcElement") + ifc_file.by_type("IfcProxy")
        else:
            elements = ifc_file.by_type("IfcElement")

        elements += ifc_file.by_type("IfcSite")
        elements = [e for e in elements if not e.is_a("IfcFeatureElement") or e.is_a("IfcSurfaceFeature")]

        if not filter_visibility:
            return elements

        # Filter by visibility in Blender.
        # We use hide_get() (user-toggled eye icon) instead of visible_get()
        # because visible_get() also considers collection/view-layer visibility
        # which incorrectly excludes objects in linked aggregate sub-collections.
        visible_elements = []
        for element in elements:
            blender_obj = tool.Ifc.get_object(element)
            if blender_obj is None:
                # No Blender object (linked aggregate copies, or not yet represented)
                # Include by default — the geometry exists in the IFC file
                visible_elements.append(element)
                continue
            if not blender_obj.hide_get():
                visible_elements.append(element)
            else:
                print(f"Skipping hidden element: {element.GlobalId if hasattr(element, 'GlobalId') else element.id()}")
        return visible_elements

    def _export_ifc_to_obj(self, ifc_file, obj_path, mtl_path, settings, serializer_settings, elements):
        """Export elements from an IFC file to OBJ format. Returns collected material names."""
        materials_collected = []
        serialiser = ifcopenshell.geom.serializers.obj(obj_path, mtl_path, settings, serializer_settings)
        serialiser.setFile(ifc_file)
        serialiser.setUnitNameAndMagnitude("METER", 1.0)
        serialiser.writeHeader()

        print(f"Exporting {len(elements)} elements to {obj_path}")
        iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count(), include=elements)
        if iterator.initialize():
            while True:
                shape = iterator.get()
                for material in shape.geometry.materials:
                    materials_collected.append(material.name)
                serialiser.write(shape)
                if not iterator.next():
                    break

        serialiser.finalize()
        return materials_collected

    def _sync_moved_object_placements(self):
        """Sync Blender object positions to IFC ObjectPlacements for all moved objects.

        This is critical for linked aggregate copies: their IFC ObjectPlacements
        are initially copies of the original's placement. After the user moves them
        in Blender, the IFC placements are stale until explicitly synced. Without
        this, the iterator with use-world-coords=True exports all copies at the
        original position.
        """
        import bonsai.core.geometry as core_geometry

        synced = 0
        for obj in bpy.data.objects:
            element = tool.Ifc.get_entity(obj)
            if element is None:
                continue
            if not element.is_a("IfcProduct"):
                continue
            try:
                if tool.Ifc.is_moved(obj):
                    core_geometry.edit_object_placement(
                        ifc=tool.Ifc,
                        geometry=tool.Geometry,
                        surveyor=tool.Surveyor,
                        obj=obj,
                        apply_scale=False,
                    )
                    synced += 1
            except Exception as e:
                print(f"Could not sync placement for {obj.name}: {e}")
        if synced:
            print(f"Synced {synced} moved object placement(s) to IFC before export")

    def _export_collection_instances_obj(self, context, output_dir):
        """Export Blender collection instances as per-parent OBJ files.

        Collection instances (empties with instance_type='COLLECTION') are purely
        Blender constructs — they don't exist in the IFC file. The ifcopenshell
        iterator ignores them entirely, so we must export their geometry via
        Blender's depsgraph which evaluates all instances with correct world transforms.

        Each collection instance parent gets its own OBJ file because obj2mesh
        cannot handle all instances in a single file ("too many patch triangles").
        """
        depsgraph = context.evaluated_depsgraph_get()

        # Find which objects are collection instance parents (visible, not hidden)
        # Skip collections that belong to linked IFC models — those are already
        # exported by _export_linked_models() via the IFC serializer.
        instance_parents = set()
        for obj in bpy.data.objects:
            if obj.instance_type == 'COLLECTION' and obj.instance_collection is not None:
                if not obj.visible_get():
                    continue
                # Check if this collection contains linked IFC objects
                coll = obj.instance_collection
                is_linked_ifc = any("guids" in child for child in coll.all_objects if child.type == 'MESH')
                if is_linked_ifc:
                    print(f"Skipping collection instance '{obj.name}' (linked IFC model, exported via IFC serializer)")
                    continue
                instance_parents.add(obj.name)

        if not instance_parents:
            return

        print(f"Found {len(instance_parents)} collection instance(s) to export")

        # Export one OBJ per collection instance parent
        identity = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        total_meshes = 0

        for parent_name in sorted(instance_parents):
            obj_path = os.path.join(output_dir, f"instance_{parent_name}.obj")
            vert_offset = 0
            mesh_count = 0

            with open(obj_path, "w") as f:
                f.write(f"# Collection instance geometry for {parent_name}\n")
                f.write("usemtl white\n\n")

                for dep_inst in depsgraph.object_instances:
                    if not dep_inst.is_instance:
                        continue
                    if dep_inst.parent is None:
                        continue
                    if dep_inst.parent.original.name != parent_name:
                        continue

                    eval_obj = dep_inst.object
                    if eval_obj.type != 'MESH':
                        continue

                    try:
                        mesh = eval_obj.to_mesh()
                    except RuntimeError:
                        continue
                    if mesh is None:
                        continue

                    matrix = dep_inst.matrix_world
                    f.write(f"g obj_{mesh_count}\n")

                    for v in mesh.vertices:
                        co = matrix @ v.co
                        f.write(f"v {co.x} {co.y} {co.z}\n")

                    mesh.calc_loop_triangles()
                    for tri in mesh.loop_triangles:
                        i0 = vert_offset + tri.vertices[0] + 1
                        i1 = vert_offset + tri.vertices[1] + 1
                        i2 = vert_offset + tri.vertices[2] + 1
                        f.write(f"f {i0} {i1} {i2}\n")

                    vert_offset += len(mesh.vertices)
                    mesh_count += 1
                    eval_obj.to_mesh_clear()

            if mesh_count == 0:
                try:
                    os.remove(obj_path)
                except OSError:
                    pass
                continue

            # Identity matrix — geometry is already at world coordinates
            linked_model_exports.append((obj_path, "", identity))
            total_meshes += mesh_count
            print(f"  {parent_name}: {mesh_count} meshes, {vert_offset} vertices")

        if total_meshes > 0:
            print(f"Exported {total_meshes} instanced meshes across {len(linked_model_exports)} file(s)")

    def execute(self, context):
        ifc_materials.clear()
        linked_model_exports.clear()

        props = tool.Blender.get_radiance_exporter_props()
        should_load_from_memory = props.should_load_from_memory
        output_dir = props.output_dir
        props.is_exporting = True

        # Sync all moved Blender object positions to IFC before export.
        # This ensures linked aggregate copies (and any other moved objects)
        # export at their correct Blender positions, not their stale IFC positions.
        if should_load_from_memory and tool.Ifc.get():
            self._sync_moved_object_placements()

        settings, serializer_settings = self._get_geom_settings()

        ifc_file: ifcopenshell.file
        if should_load_from_memory:
            ifc_file = tool.Ifc.get()
        else:
            ifc_file_path = props.ifc_file
            ifc_file = ifcopenshell.open(ifc_file_path)

        # --- Export main model ---
        obj_file_path = os.path.join(output_dir, "model.obj")
        mtl_file_path = os.path.join(output_dir, "model.mtl")

        visible_elements = self._get_exportable_elements(ifc_file, filter_visibility=should_load_from_memory)
        mats = self._export_ifc_to_obj(ifc_file, obj_file_path, mtl_file_path, settings, serializer_settings, visible_elements)
        ifc_materials.extend(mats)

        self.report({"INFO"}, f"Exported main model OBJ to: {obj_file_path}")

        # --- Export linked models (external IFC files) ---
        if should_load_from_memory and tool.Ifc.get():
            self._export_linked_models(ifc_file, output_dir, settings, serializer_settings)

        # --- Export collection instances (Blender-level linked copies) ---
        if should_load_from_memory:
            self._export_collection_instances_obj(context, output_dir)

        # --- Export non-IFC Blender meshes (plain geometry with no IFC entity) ---
        if should_load_from_memory:
            self._export_non_ifc_meshes(context, output_dir)

        props.is_exporting = False
        total_linked = len(linked_model_exports)
        if total_linked:
            self.report({"INFO"}, f"Also exported {total_linked} linked/instanced model(s)")
        return {"FINISHED"}

    def _export_non_ifc_meshes(self, context, output_dir):
        """Export visible Blender mesh objects that have no IFC entity.

        These are plain Blender geometry (e.g. manually added planes, cubes)
        that don't exist in any IFC file. They are skipped by the IFC iterator
        and by the collection instance exporter, so we handle them separately.
        """
        non_ifc_meshes = []
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            if not obj.visible_get():
                continue
            # Skip objects that have an IFC entity (handled by main/linked IFC export)
            if tool.Ifc.get_entity(obj) is not None:
                continue
            # Skip objects inside instanced collections (handled by collection instance export)
            if any(col.library for col in obj.users_collection):
                continue
            # Skip linked IFC element objects (have "guids" custom prop)
            if "guids" in obj:
                continue
            non_ifc_meshes.append(obj)

        if not non_ifc_meshes:
            return

        obj_path = os.path.join(output_dir, "blender_meshes.obj")
        vert_offset = 0
        mesh_count = 0
        identity = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

        depsgraph = context.evaluated_depsgraph_get()

        with open(obj_path, "w") as f:
            f.write("# Non-IFC Blender mesh geometry\n")
            f.write("usemtl white\n\n")

            for obj in non_ifc_meshes:
                eval_obj = obj.evaluated_get(depsgraph)
                try:
                    mesh = eval_obj.to_mesh()
                except RuntimeError:
                    continue
                if mesh is None:
                    continue

                matrix = obj.matrix_world
                f.write(f"g {obj.name}\n")

                for v in mesh.vertices:
                    co = matrix @ v.co
                    f.write(f"v {co.x} {co.y} {co.z}\n")

                mesh.calc_loop_triangles()
                for tri in mesh.loop_triangles:
                    i0 = vert_offset + tri.vertices[0] + 1
                    i1 = vert_offset + tri.vertices[1] + 1
                    i2 = vert_offset + tri.vertices[2] + 1
                    f.write(f"f {i0} {i1} {i2}\n")

                vert_offset += len(mesh.vertices)
                mesh_count += 1
                eval_obj.to_mesh_clear()

        if mesh_count == 0:
            try:
                os.remove(obj_path)
            except OSError:
                pass
            return

        linked_model_exports.append((obj_path, "", identity))
        print(f"Exported {mesh_count} non-IFC Blender mesh(es) ({vert_offset} vertices)")

    def _export_linked_models(self, main_ifc_file, output_dir, settings, serializer_settings):
        """Detect and export all linked IFC models."""
        try:
            project_props = tool.Project.get_project_props()
        except Exception:
            print("Could not access project properties for linked models")
            return

        for idx, link in enumerate(project_props.links):
            if not link.is_loaded:
                print(f"Skipping linked model '{link.name}' (not loaded)")
                continue

            # Check if the link's empty handle is hidden in Blender
            try:
                link_empty = tool.Project.get_link_empty_handle(link)
                if link_empty is not None and not link_empty.visible_get():
                    print(f"Skipping linked model '{link.name}' (hidden in viewport)")
                    continue
            except Exception:
                pass  # If we can't check visibility, export anyway

            try:
                filepath = Path(tool.Ifc.resolve_uri(link.filepath))
            except Exception as e:
                print(f"Could not resolve path for linked model '{link.name}': {e}")
                continue

            if not filepath.exists():
                print(f"Linked IFC file not found: {filepath}")
                continue

            print(f"Exporting linked model {idx}: {filepath.name}")
            try:
                linked_ifc = ifcopenshell.open(str(filepath))
            except Exception as e:
                print(f"  Failed to open linked IFC: {e}")
                continue

            link_obj_path = os.path.join(output_dir, f"linked_{idx}.obj")
            link_mtl_path = os.path.join(output_dir, f"linked_{idx}.mtl")

            # For linked models we don't filter by Blender visibility
            # (their objects are collection instances, not individually tracked)
            elements = self._get_exportable_elements(linked_ifc, filter_visibility=False)
            if not elements:
                print(f"  No exportable elements found in linked model")
                continue

            mats = self._export_ifc_to_obj(
                linked_ifc, link_obj_path, link_mtl_path, settings, serializer_settings, elements
            )
            ifc_materials.extend(mats)

            # Get the link transformation matrix
            try:
                link_matrix = tool.Project.calculate_link_matrix(link)
                matrix_list = [list(row) for row in link_matrix]
            except Exception as e:
                print(f"  Could not calculate link matrix: {e}, using identity")
                matrix_list = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

            linked_model_exports.append((link_obj_path, link_mtl_path, matrix_list))
            print(f"  Exported {len(elements)} elements from linked model '{link.name}'")


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

        # Final safety: if up is still degenerate, default to world Z
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

        # Get camera data (must be on main thread — accesses Blender objects)
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
                "year": sun_props.year, "month": sun_props.month, "day": sun_props.day,
                "hour": sun_props.hour, "minute": sun_props.minute,
                "latitude": sun_props.latitude, "longitude": sun_props.longitude,
                "UTC_zone": sun_props.UTC_zone, "sun_year": sun_pos_props.year,
                "sky_condition": props.sky_condition,
                "ground_reflectance": props.ground_reflectance,
                "turbidity": props.turbidity,
            }

        # Collect IES light data (must be on main thread — accesses Blender pointer props)
        # Each entry has a list of positions (one per target empty) to support collection mode
        ies_light_data = []  # list of dicts with all needed data
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

            ies_light_data.append({
                "ies_file_path": ies_light.ies_file_path,
                "lamp_type": ies_light.lamp_type,
                "lamp_color": ies_light.lamp_color,
                "multiply_factor": ies_light.multiply_factor,
                "radius": ies_light.radius,
                "rotation_z": ies_light.rotation_z,
                "positions": positions,
                "is_enabled": ies_light.is_enabled,
            })

        # Collect material mapping data (must be on main thread)
        material_mappings = []
        for m in props.materials:
            material_mappings.append({
                "style_id": m.style_id,
                "is_mapped": m.is_mapped,
                "category": m.category,
                "subcategory": m.subcategory,
            })

        # Snapshot linked_model_exports (it's a module-level list)
        linked_exports_snapshot = list(linked_model_exports)

        # All Blender data collected — now launch background thread
        props.is_preparing = True
        self._start_time = time.time()
        self._error = None

        global scene
        scene = None

        self._thread = threading.Thread(
            target=self._prepare_worker,
            args=(
                output_dir, obj_file_path, sky_file_path,
                use_hdr, choose_hdr_image, hdr_image_path, hdr_mask_path, sky_map_cal_path,
                sky_data, ies_light_data, material_mappings,
                linked_exports_snapshot,
                camera_position, camera_direction, camera_up,
                camera_type, camera_fov, camera_ortho_scale,
                aspect_ratio,
            ),
            daemon=True,
        )
        self._thread.start()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        self.report({"INFO"}, "Scene preparation started in background...")
        context.window.cursor_set('WAIT')
        return {"RUNNING_MODAL"}

    def _prepare_worker(
        self, output_dir, obj_file_path, sky_file_path,
        use_hdr, choose_hdr_image, hdr_image_path, hdr_mask_path, sky_map_cal_path,
        sky_data, ies_light_data, material_mappings,
        linked_exports_snapshot,
        camera_position, camera_direction, camera_up,
        camera_type, camera_fov, camera_ortho_scale,
        aspect_ratio,
    ):
        """Runs in a background thread — no Blender API calls allowed here."""
        try:
            self._do_prepare(
                output_dir, obj_file_path, sky_file_path,
                use_hdr, choose_hdr_image, hdr_image_path, hdr_mask_path, sky_map_cal_path,
                sky_data, ies_light_data, material_mappings,
                linked_exports_snapshot,
                camera_position, camera_direction, camera_up,
                camera_type, camera_fov, camera_ortho_scale,
                aspect_ratio,
            )
        except Exception as e:
            self._error = str(e)
            import traceback
            traceback.print_exc()

    def _do_prepare(
        self, output_dir, obj_file_path, sky_file_path,
        use_hdr, choose_hdr_image, hdr_image_path, hdr_mask_path, sky_map_cal_path,
        sky_data, ies_light_data, material_mappings,
        linked_exports_snapshot,
        camera_position, camera_direction, camera_up,
        camera_type, camera_fov, camera_ortho_scale,
        aspect_ratio,
    ):
        """The actual preparation logic (no Blender API)."""
        global scene

        # --- Generate sky file ---
        if sky_data is not None:
            dt = datetime(sky_data["year"], sky_data["month"], sky_data["day"],
                          sky_data["hour"], sky_data["minute"])

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
                        abs(link_matrix[i][j] - (1.0 if i == j else 0.0)) < 1e-6
                        for i in range(4) for j in range(4)
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
        scene = new_scene
        print("Scene preparation complete.")

    def modal(self, context, event):
        if event.type == 'TIMER':
            if self._thread is not None and self._thread.is_alive():
                return {"RUNNING_MODAL"}

            # Thread finished — clean up
            self._cleanup_timer(context)
            props = tool.Blender.get_radiance_exporter_props()
            props.is_preparing = False
            context.window.cursor_set('DEFAULT')

            if self._error:
                self.report({"ERROR"}, f"Scene preparation failed: {self._error}")
                return {"CANCELLED"}

            elapsed = time.time() - self._start_time
            self.report({"INFO"}, f"Radiance scene prepared successfully in {elapsed:.1f}s")
            print(f"Scene preparation completed in {elapsed:.2f} seconds")
            return {"FINISHED"}

        elif event.type == 'ESC':
            self._cleanup_timer(context)
            props = tool.Blender.get_radiance_exporter_props()
            props.is_preparing = False
            context.window.cursor_set('DEFAULT')
            self.report({"WARNING"}, "Scene preparation cannot be cancelled mid-operation")
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def _cleanup_timer(self, context):
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None


class RadianceRender(bpy.types.Operator):
    """Radiance Rendering (runs in background thread)"""

    bl_idname = "render_scene.radiance"
    bl_label = "Render"
    bl_description = "Renders the scene using Radiance"

    _timer = None
    _thread: Union[threading.Thread, None] = None
    _result_image: Union[bytes, None] = None
    _error: Union[str, None] = None
    _start_time: float = 0.0

    @classmethod
    def poll(cls, context):
        props = tool.Blender.get_radiance_exporter_props()
        if props.is_rendering:
            cls.poll_message_set("A render is already in progress.")
            return False
        if scene is None:
            cls.poll_message_set("Radiance scene not prepared. Please run 'Prepare Scene' (Step 2) first.")
            return False
        return True

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        resolution_x, resolution_y = props.radiance_resolution_x, props.radiance_resolution_y

        context.scene.render.resolution_x = resolution_x
        context.scene.render.resolution_y = resolution_y

        quality = props.radiance_quality.upper()
        detail = props.radiance_detail.upper()
        variability = props.radiance_variability.upper()
        ambient_bounces = props.ambient_bounces
        output_dir = props.output_dir

        props.is_rendering = True
        self._start_time = time.time()
        self._result_image = None
        self._error = None

        # Launch render in a background thread
        self._thread = threading.Thread(
            target=self._render_worker,
            args=(scene, output_dir, resolution_x, resolution_y, quality, detail, variability, ambient_bounces),
            daemon=True,
        )
        self._thread.start()

        # Set up a timer to poll for completion
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        self.report({"INFO"}, "Radiance render started in background...")
        context.window.cursor_set('WAIT')
        return {"RUNNING_MODAL"}

    def _render_worker(self, render_scene, output_dir, res_x, res_y, quality, detail, variability, ambient_bounces):
        """Runs in a background thread — no Blender API calls allowed here."""
        cwd_saved = os.getcwd()
        try:
            os.chdir(output_dir)
            self._result_image = pr.render(
                render_scene,
                ambbounce=ambient_bounces,
                resolution=(res_x, res_y),
                quality=quality,
                detail=detail,
                variability=variability,
                nproc=multiprocessing.cpu_count(),
            )
        except Exception as e:
            self._error = str(e)
        finally:
            os.chdir(cwd_saved)

    def modal(self, context, event):
        if event.type == 'TIMER':
            if self._thread is not None and self._thread.is_alive():
                # Still running — keep waiting
                return {"RUNNING_MODAL"}

            # Thread finished — clean up timer
            self._cleanup_timer(context)
            props = tool.Blender.get_radiance_exporter_props()
            props.is_rendering = False
            context.window.cursor_set('DEFAULT')

            if self._error:
                self.report({"ERROR"}, f"Radiance render failed: {self._error}")
                return {"CANCELLED"}

            elapsed = time.time() - self._start_time
            print(f"Render completed in {elapsed:.2f} seconds")

            # Write output files (safe on main thread)
            output_dir = props.output_dir
            output_file_name = props.output_file_name
            output_file_format = props.output_file_format

            output_hdr_path = os.path.join(output_dir, f"{output_file_name}.hdr")
            print(f"Saving HDR output to: {output_hdr_path}")
            with open(output_hdr_path, "wb") as wtr:
                wtr.write(self._result_image)

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

            # Force UI redraw so the render button re-enables
            for area in context.screen.areas:
                area.tag_redraw()

            return {"FINISHED"}

        elif event.type == 'ESC':
            # User pressed Escape — we can't kill the thread, but we can stop waiting
            self._cleanup_timer(context)
            props = tool.Blender.get_radiance_exporter_props()
            props.is_rendering = False
            context.window.cursor_set('DEFAULT')
            self.report({"WARNING"}, "Render cancelled by user. Background process may still be running.")
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def _cleanup_timer(self, context):
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None


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
            fc_output_name = props.false_color_output_name
            fc_hdr_path = os.path.join(output_dir, f"{fc_output_name}.hdr")

            # Get path to bundled falsecolor executable
            light_module_dir = os.path.dirname(__file__)
            falsecolor_exe = os.path.join(light_module_dir, "Radiance", "bin", "falsecolor.exe")
            radiance_lib = os.path.join(light_module_dir, "Radiance", "lib")
            radiance_bin_dir = os.path.join(light_module_dir, "Radiance", "bin")

            print(f"Looking for bundled falsecolor at: {falsecolor_exe}")

            if os.path.exists(falsecolor_exe):
                falsecolor_bin = falsecolor_exe
                print(f"Using bundled falsecolor: {falsecolor_bin}")
            else:
                # Try to find falsecolor in system PATH
                import shutil

                system_falsecolor = shutil.which("falsecolor.exe") or shutil.which("falsecolor")
                if system_falsecolor:
                    falsecolor_bin = system_falsecolor
                    radiance_bin_dir = os.path.dirname(system_falsecolor)
                    radiance_lib = os.path.join(os.path.dirname(radiance_bin_dir), "lib")
                    print(f"Using system falsecolor: {falsecolor_bin}")
                else:
                    falsecolor_bin = "falsecolor"
                    print(f"Warning: falsecolor.exe not found in bundle or system PATH, will try system PATH")

            # Build command line arguments for falsecolor
            cmd = [falsecolor_bin]
            cmd.extend(["-m", str(multiplier)])
            cmd.extend(["-s", fc_scale])
            cmd.extend(["-n", str(props.false_color_steps)])
            cmd.extend(["-l", props.false_color_label])

            # Determine contour mode and build command accordingly
            if props.false_color_contour_lines:
                if props.false_color_contour_mode == "WITH_BG":
                    # Contour lines with background - use -cl and -ip
                    print("Generating false color with contour lines (with background)...")
                    cmd.append("-cl")
                    cmd.append("-ip")
                    cmd.append(hdr_path)
                else:  # WITHOUT_BG
                    # Contour lines only (with legend but no colored background)
                    print("Generating false color with contour lines only (with legend, no background)...")
                    cmd.append("-cl")
                    cmd.append("-i")
                    cmd.append(hdr_path)
            else:
                # No contour lines - standard false color with -ip
                print("Generating standard false color image...")
                cmd.append("-ip")
                cmd.append(hdr_path)

            print(f"Running falsecolor command: {' '.join(cmd)}")
            print(f"Using falsecolor binary: {falsecolor_bin}")

            # Setup environment for Radiance tools
            env = os.environ.copy()

            # Add Radiance bin directory to PATH so falsecolor can find its dependencies
            if radiance_bin_dir and os.path.exists(radiance_bin_dir):
                env["PATH"] = radiance_bin_dir + os.pathsep + env.get("PATH", "")
                print(f"Added to PATH: {radiance_bin_dir}")

            # Set RAYPATH for Radiance library files
            if os.path.exists(radiance_lib):
                env["RAYPATH"] = "." + os.pathsep + radiance_lib
                print(f"Set RAYPATH: {radiance_lib}")
            else:
                print(f"Note: Radiance lib folder not found at {radiance_lib}")

            # Execute falsecolor and capture output
            # Use cwd=output_dir to ensure falsecolor writes to the correct location
            result = subprocess.run(cmd, capture_output=True, check=True, env=env, cwd=output_dir)
            fc_image = result.stdout

            print(f"Saving false color HDR to: {fc_hdr_path}")
            with open(fc_hdr_path, "wb") as f:
                f.write(fc_image)

            print(f"False color HDR generated successfully: {fc_hdr_path}")
            self.report({"INFO"}, f"False color image generated: {fc_hdr_path}")

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

        except subprocess.CalledProcessError as e:
            error_msg = f"falsecolor failed: {e.stderr.decode() if e.stderr else str(e)}"
            print(f"ERROR: {error_msg}")
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}
        except FileNotFoundError as fnf_error:
            # Check if falsecolor was not found
            if "falsecolor" in str(fnf_error).lower() or not os.path.exists(falsecolor_exe):
                error_msg = "falsecolor not found! Please install Radiance and add it to your system PATH"
            else:
                error_msg = f"falsecolor binary not found at: {falsecolor_exe}. Please ensure the Radiance/bin folder is present in the light module directory."
            print(f"ERROR: {error_msg}")
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}
        except Exception as e:
            # Check if it's a falsecolor not found error
            if "falsecolor" in str(e).lower() or isinstance(e, FileNotFoundError):
                error_msg = "falsecolor not found! Please install Radiance and add it to your system PATH"
            else:
                error_msg = f"Failed to generate false color image: {str(e)}"

            self.report({"ERROR"}, error_msg)
            print(f"ERROR: {error_msg}")
            print(f"Traceback:")
            import traceback

            traceback.print_exc()
            return {"CANCELLED"}


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

    # Only include non-zero rotations
    if abs(rx) > 1e-6:
        parts.append(f"-rx {rx:.6f}")
    if abs(ry) > 1e-6:
        parts.append(f"-ry {ry:.6f}")
    if abs(rz) > 1e-6:
        parts.append(f"-rz {rz:.6f}")

    # Translation is always applied last (rightmost in xform, applied first to geometry)
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

    use_current_location: bpy.props.BoolProperty(options={"SKIP_SAVE"})

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
        try:
            data = context.space_data.context_pointer_get("data")
        except Exception:
            self.report({"ERROR"}, "Could not access context data for enum search.")
            return {"CANCELLED"}
        if data is None:
            self.report({"ERROR"}, "No context data available for enum search.")
            return {"CANCELLED"}
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

        ies_path = Path(bpy.path.abspath(ies_file_path))
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
        # Store as relative path if the blend file is saved
        if bpy.data.filepath:
            ies_light.ies_file_path = bpy.path.relpath(self.filepath)
        else:
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


class CleanupRadianceFiles(bpy.types.Operator):
    """Delete all generated Radiance files from the output directory"""

    bl_idname = "radiance.cleanup_files"
    bl_label = "Cleanup Radiance Files"
    bl_description = "Remove all generated files (OBJ, MTL, RTM, RAD, HDR, TIFF, DAT) from the output directory"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = tool.Blender.get_radiance_exporter_props()
        if not props.output_dir:
            cls.poll_message_set("Output directory is not set.")
            return False
        return True

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        output_dir = props.output_dir

        if not os.path.isdir(output_dir):
            self.report({"WARNING"}, f"Output directory does not exist: {output_dir}")
            return {"CANCELLED"}

        cleanup_patterns = (
            "model.obj", "model.mtl", "model.rtm",
            "sky.rad", "materials.rad", "scene.rad",
            "ascene.oct", "mascene.oct", "ascene.amb",
        )
        cleanup_extensions = (".hdr", ".tiff", ".rad", ".dat")
        # Also match generated instance/linked files: instance_*.obj/rtm, linked_*.obj/rtm
        cleanup_prefixes = ("instance_", "linked_")

        removed = 0
        for filename in os.listdir(output_dir):
            filepath = os.path.join(output_dir, filename)
            if not os.path.isfile(filepath):
                continue
            is_generated = (
                filename in cleanup_patterns
                or os.path.splitext(filename)[1].lower() in cleanup_extensions
                or any(filename.startswith(p) for p in cleanup_prefixes)
            )
            if is_generated:
                try:
                    os.remove(filepath)
                    removed += 1
                except OSError as e:
                    print(f"Failed to remove {filepath}: {e}")

        # Reset the global scene reference
        global scene
        scene = None

        self.report({"INFO"}, f"Cleaned up {removed} generated files from {output_dir}")
        return {"FINISHED"}

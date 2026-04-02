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
import multiprocessing
import os
from pathlib import Path
from typing import Union

import bpy
import ifcopenshell
import ifcopenshell.geom

import bonsai.tool as tool
from bonsai.bim.module.light.shared import ifc_materials, linked_model_exports


class ExportOBJ(bpy.types.Operator):
    """Exports the IFC File to OBJ"""

    bl_idname = "export_scene.radiance"
    bl_label = "Export"
    bl_description = "Export the IFC to OBJ"

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC file loaded in Bonsai.")
            return False
        props = tool.Blender.get_radiance_exporter_props()
        if not props.output_dir:
            cls.poll_message_set("Output directory is not set.")
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

    def execute(self, context):
        ifc_materials.clear()
        linked_model_exports.clear()

        props = tool.Blender.get_radiance_exporter_props()
        output_dir = props.output_dir
        props.is_exporting = True

        # Sync all moved Blender object positions to IFC before export.
        self._sync_moved_object_placements()

        settings, serializer_settings = self._get_geom_settings()

        ifc_file = tool.Ifc.get()

        # --- Export main model ---
        obj_file_path = os.path.join(output_dir, "model.obj")
        mtl_file_path = os.path.join(output_dir, "model.mtl")

        visible_elements = self._get_exportable_elements(ifc_file, filter_visibility=True)
        mats = self._export_ifc_to_obj(ifc_file, obj_file_path, mtl_file_path, settings, serializer_settings, visible_elements)
        ifc_materials.extend(mats)

        self.report({"INFO"}, f"Exported main model OBJ to: {obj_file_path}")

        # --- Export linked models (external IFC files) ---
        self._export_linked_models(ifc_file, output_dir, settings, serializer_settings)

        # --- Export collection instances (Blender-level linked copies) ---
        self._export_collection_instances_obj(context, output_dir)

        # --- Export non-IFC Blender meshes (plain geometry with no IFC entity) ---
        self._export_non_ifc_meshes(context, output_dir)

        props.is_exporting = False
        total_linked = len(linked_model_exports)
        if total_linked:
            self.report({"INFO"}, f"Also exported {total_linked} linked/instanced model(s)")
        return {"FINISHED"}

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
        import bonsai.bim.module.light.shared as shared

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
        cleanup_prefixes = ("instance_", "linked_", "blender_meshes")

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
        shared.scene = None

        self.report({"INFO"}, f"Cleaned up {removed} generated files from {output_dir}")
        return {"FINISHED"}

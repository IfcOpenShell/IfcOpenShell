# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import json
import os
import logging
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.selector
import ifcopenshell.api.project
import ifcopenshell.guid
from mathutils import Matrix
from bonsai.bim.ifc import IfcStore
import bonsai.tool as tool
import bonsai.bim.import_ifc as import_ifc
import bonsai.bim.handler


def get_clipboard_path(filename):
    return tool.Blender.get_data_dir_path(filename).__str__()


class CopyToClipboard(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_to_clipboard"
    bl_label = "Copy IFC Elements"
    bl_description = "Copy selected IFC elements to clipboard with all dependencies"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.selected_objects
    
    def extract_elements(self, source_file: ifcopenshell.file, query: str) -> ifcopenshell.file:
        """
        Extract elements from source IFC file into a new library file.
        
        Follows the logic from ifcpatch ExtractElements recipe to create a minimal
        IFC file containing only the queried elements and their dependencies.
        
        :param source_file: The source IFC file to extract from
        :param query: The selector query for elements to extract
        :return: New IFC file containing only extracted elements
        """
        # Initialize new file and tracking structures
        new_file = ifcopenshell.file(schema_version=source_file.schema_version)
        contained_ins = {}  # spatial containment relationships
        aggregates = {}  # decomposition relationships
        reuse_identities = {}  # identity map for append_asset
        owner_history = None
        
        # Copy owner history if exists
        for oh in source_file.by_type("IfcOwnerHistory"):
            owner_history = new_file.add(oh)
            break
        
        def append_asset(element):
            """Add element to new file, reusing if already added."""
            if element.is_a("IfcProject"):
                return new_file.add(element)
            return ifcopenshell.api.project.append_asset(
                new_file,
                library=source_file,
                element=element,
                reuse_identities=reuse_identities,
                assume_asset_uniqueness_by_name=False,  # Preserve distinct assets
                use_geolocation=False,  # Use local coordinates without geolocation transformation
            )
        
        def add_spatial_structures(element, new_element):
            """Track spatial containment for later relationship creation."""
            for rel in getattr(element, "ContainedInStructure", []):
                spatial_element = rel.RelatingStructure
                new_spatial_element = append_asset(spatial_element)
                contained_ins.setdefault(spatial_element.GlobalId, set()).add(new_element)
                add_decomposition_parents(spatial_element, new_spatial_element)
        
        def add_decomposition_parents(element, new_element):
            """Track decomposition relationships for later creation."""
            for rel in element.Decomposes:
                parent = rel.RelatingObject
                new_parent = append_asset(parent)
                aggregates.setdefault(parent.GlobalId, set()).add(new_element)
                add_decomposition_parents(parent, new_parent)
                add_spatial_structures(parent, new_parent)
        
        def add_element(element):
            """Add element and all its spatial/decomposition relationships."""
            new_element = append_asset(element)
            if not new_element:
                return
            add_spatial_structures(element, new_element)
            add_decomposition_parents(element, new_element)
        
        # Add project first
        add_element(source_file.by_type("IfcProject")[0])
        
        # Extract and add all elements matching query with progress reporting
        elements = list(ifcopenshell.util.selector.filter_elements(source_file, query))
        total = len(elements)
        
        for idx, element in enumerate(elements):
            if idx % max(1, total // 20) == 0:
                percent = int((idx / total) * 100)
                bpy.context.window_manager.progress_update(percent)
            add_element(element)
        
        # Create spatial tree relationships
        for relating_structure_guid, related_elements in contained_ins.items():
            new_file.createIfcRelContainedInSpatialStructure(
                ifcopenshell.guid.new(),
                owner_history,
                None,
                None,
                list(related_elements),
                new_file.by_guid(relating_structure_guid),
            )
        
        for relating_object_guid, related_objects in aggregates.items():
            new_file.createIfcRelAggregates(
                ifcopenshell.guid.new(),
                owner_history,
                None,
                None,
                new_file.by_guid(relating_object_guid),
                list(related_objects),
            )
        

        
        return new_file

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        elements_to_copy = []
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            
            if element.is_a("IfcGridAxis"):
                parent_grid = None
                if element.PartOfU:
                    parent_grid = element.PartOfU[0]
                elif element.PartOfV:
                    parent_grid = element.PartOfV[0]
                elif element.PartOfW:
                    parent_grid = element.PartOfW[0]
                
                if parent_grid:
                    element = parent_grid
                else:
                    continue
            
            # Only entities with GlobalId can be copied
            if not element.GlobalId:
                continue
            
            if not any(e.id() == element.id() for obj, e in elements_to_copy):
                elements_to_copy.append((obj, element))
        
        if not elements_to_copy:
            self.report({"WARNING"}, "No IFC elements selected")
            return {"CANCELLED"}
        
        # Show progress for large operations
        total = len(elements_to_copy)
        show_progress = total > 20
        if show_progress:
            bpy.context.window_manager.progress_begin(0, 100)
        
        global_ids = [element.GlobalId for obj, element in elements_to_copy]
        query = f"GlobalId = {', '.join(global_ids)}"
        
        # Extract elements into library file using our implementation
        # This avoids making ifcpatch dependent on Blender
        library = self.extract_elements(ifc_file, query)
                
        clipboard_ifc = get_clipboard_path("bonsai_clipboard.ifc")
        library.write(clipboard_ifc)
        
        clipboard_data = {
            "version": 1,
            "schema": ifc_file.schema,
            "elements": []
        }
        
        for obj, element in elements_to_copy:
            matrix = obj.matrix_world.copy()
            container_element = ifcopenshell.util.element.get_container(element)
            container_name = container_element.Name if container_element else None
            container_class = container_element.is_a() if container_element else None
            
            clipboard_data["elements"].append({
                "global_id": element.GlobalId,
                "ifc_class": element.is_a(),
                "name": element.Name or "",
                "matrix": [float(v) for row in matrix for v in row],
                "container_name": container_name,
                "container_class": container_class,
            })
        
        clipboard_json = get_clipboard_path("bonsai_clipboard.json")
        with open(clipboard_json, "w") as f:
            json.dump(clipboard_data, f, indent=2)
        
        if show_progress:
            bpy.context.window_manager.progress_end()
        
        # Ensure clipboard UI sections are initialized
        context.scene.BIMClipboardProperties.ensure_sections()
        
        self.report({"INFO"}, f"Copied {len(clipboard_data['elements'])} element(s)")
        return {"FINISHED"}


class PasteFromClipboard(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.paste_from_clipboard"
    bl_label = "Paste IFC Elements"
    bl_description = "Paste IFC elements from clipboard. Creates Blender objects in active container"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        clipboard_json = get_clipboard_path("bonsai_clipboard.json")
        return tool.Ifc.get() and os.path.exists(clipboard_json)

    def _execute(self, context):
        clipboard_json = get_clipboard_path("bonsai_clipboard.json")
        clipboard_ifc = get_clipboard_path("bonsai_clipboard.ifc")
        
        with open(clipboard_json, "r") as f:
            clipboard_data = json.load(f)
        
        if not os.path.exists(clipboard_ifc):
            self.report({"ERROR"}, "Clipboard library file not found")
            return {"CANCELLED"}
        
        # Set clipboard.ifc as the library file
        IfcStore.library_file = ifcopenshell.open(clipboard_ifc)
        IfcStore.library_path = clipboard_ifc
        
        # Clean up broken material associations in clipboard file (RelatingMaterial = None)
        # This happens when materials don't get fully copied
        for rel in IfcStore.library_file.by_type("IfcRelAssociatesMaterial"):
            if rel.RelatingMaterial is None:
                IfcStore.library_file.remove(rel)
        
        # Show progress for large operations
        total = len(clipboard_data["elements"])
        show_progress = total > 20
        if show_progress:
            bpy.context.window_manager.progress_begin(0, 100)
        
        ifc_file = tool.Ifc.get()
        
        # Track elements with GlobalId conflicts that need regeneration IN THE LIBRARY FILE
        # We must regenerate GUIDs BEFORE appending, otherwise append_asset will reuse existing elements
        elements_needing_new_guid = []
        failed_elements = []
        
        # First pass: identify and regenerate conflicting GlobalIds in the library file
        for elem_data in clipboard_data["elements"]:
            # Find element in clipboard library by GUID
            try:
                library_element = IfcStore.library_file.by_guid(elem_data["global_id"])
            except RuntimeError as e:
                failed_elements.append(f"{elem_data.get('ifc_class', 'Unknown')} (GUID not found: {e})")
                continue
            
            # Check if GlobalId already exists in the target file
            try:
                existing_element = ifc_file.by_guid(elem_data["global_id"])
                # Conflict detected! Regenerate GlobalId in the library file NOW
                old_guid = library_element.GlobalId
                new_guid = ifcopenshell.guid.new()
                library_element.GlobalId = new_guid
                elem_data["global_id"] = new_guid  # Update the clipboard data too
                elements_needing_new_guid.append((old_guid, new_guid, library_element.is_a()))
            except RuntimeError:
                # No conflict, proceed normally with original GlobalId
                pass
        
        # Second pass: append each element from clipboard using the standard library append flow
        pasted_count = 0
        created_containers = {}  # Cache for created containers: {(class, name): element}
        
        for idx, elem_data in enumerate(clipboard_data["elements"]):
            if show_progress and idx % max(1, total // 10) == 0:
                percent = int((idx / total) * 100)
                bpy.context.window_manager.progress_update(percent)
            
            try:
                library_element = IfcStore.library_file.by_guid(elem_data["global_id"])
            except RuntimeError as e:
                failed_elements.append(f"{elem_data.get('ifc_class', 'Unknown')} (GUID not found after regeneration: {e})")
                continue
            
            try:
                bpy.ops.bim.append_library_element(
                    definition=library_element.id(), 
                    use_geolocation=False,
                    assume_unique_by_name=False
                )
                pasted_count += 1
                
                container_name = elem_data.get("container_name")
                container_class = elem_data.get("container_class")
                
                if container_name and container_class:
                    pasted_element = ifc_file.by_guid(elem_data["global_id"])
                    pasted_obj = tool.Ifc.get_object(pasted_element)
                    
                    if not pasted_obj:
                        continue
                    
                    container = None
                    cache_key = (container_class, container_name)
                    
                    if cache_key in created_containers:
                        container = created_containers[cache_key]
                    else:
                        for element in ifc_file.by_type(container_class):
                            if element.Name == container_name:
                                container = element
                                break
                        
                        if not container:
                            parent = self.find_container_parent(ifc_file, container_class)
                            parent_obj = tool.Ifc.get_object(parent) if parent else None
                            
                            if parent_obj:
                                bpy.ops.bim.add_part_to_object(
                                    part_class=container_class,
                                    part_name=container_name,
                                    element=parent.id()
                                )
                                for element in ifc_file.by_type(container_class):
                                    if element.Name == container_name and element not in created_containers.values():
                                        container = element
                                        break
                        
                        if container:
                            created_containers[cache_key] = container
                    
                    if container:
                        for obj in context.selected_objects:
                            obj.select_set(False)
                        pasted_obj.select_set(True)
                        context.view_layer.objects.active = pasted_obj
                        
                        bpy.ops.bim.assign_container(container=container.id())
                    
            except Exception as e:
                failed_elements.append(f"{library_element.is_a()} {elem_data['global_id']} (Error: {str(e)[:100]})")
                continue
        
        if show_progress:
            bpy.context.window_manager.progress_update(100)
            bpy.context.window_manager.progress_end()
        
        # Report results
        if pasted_count > 0:
            msg = f"Pasted {pasted_count} element(s)"
            if elements_needing_new_guid:
                msg += f" ({len(elements_needing_new_guid)} with regenerated GlobalIds)"
            self.report({"INFO"}, msg)
        if failed_elements:
            if pasted_count == 0:
                self.report({"ERROR"}, f"Failed to paste all {len(failed_elements)} element(s) - see console")
        
        return {"FINISHED"}
    
    def find_container_parent(self, ifc_file, container_class):
        """Find appropriate parent for a spatial container based on hierarchy."""
        hierarchy = {
            "IfcSpace": "IfcBuildingStorey",
            "IfcBuildingStorey": "IfcBuilding",
            "IfcBuilding": "IfcSite",
            "IfcSite": "IfcProject",
        }
        
        parent_class = hierarchy.get(container_class)
        if not parent_class:
            for fallback_class in ["IfcBuildingStorey", "IfcBuilding", "IfcSite"]:
                parents = ifc_file.by_type(fallback_class)
                if parents:
                    return parents[0]
            return None
        
        parents = ifc_file.by_type(parent_class)
        if parents:
            return parents[0]
        
        if parent_class == "IfcProject":
            projects = ifc_file.by_type("IfcProject")
            return projects[0] if projects else None
        
        grandparent = self.find_container_parent(ifc_file, parent_class)
        if not grandparent:
            return None
            
        grandparent_obj = tool.Ifc.get_object(grandparent)
        if not grandparent_obj:
            return None
        
        bpy.ops.bim.add_part_to_object(
            part_class=parent_class,
            part_name=f"Default {parent_class.replace('Ifc', '')}",
            element=grandparent.id()
        )
        
        parents = ifc_file.by_type(parent_class)
        return parents[-1] if parents else None  # Return the most recently created one





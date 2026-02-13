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


def strip_georeferencing(ifc_file: ifcopenshell.file) -> None:
    for map_conversion in ifc_file.by_type("IfcMapConversion"):
        ifc_file.remove(map_conversion)
    
    for projected_crs in ifc_file.by_type("IfcProjectedCRS"):
        ifc_file.remove(projected_crs)
    
    for context in ifc_file.by_type("IfcGeometricRepresentationContext"):
        if context.TrueNorth:
            context.TrueNorth = None
    
    for project in ifc_file.by_type("IfcProject"):
        for rel in project.IsDefinedBy or []:
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition
                if pset.is_a("IfcPropertySet") and pset.Name == "ePSet_ProjectedCRS":
                    ifc_file.remove(rel)
                    ifc_file.remove(pset)


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
        
        strip_georeferencing(library)
        
        for rel in library.by_type("IfcRelDefinesByProperties"):
            library.remove(rel)
        
        for pset in list(library.by_type("IfcPropertySet")):
            library.remove(pset)
        for qset in list(library.by_type("IfcElementQuantity")):
            library.remove(qset)
        
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
            
            clipboard_data["elements"].append({
                "global_id": element.GlobalId,
                "ifc_class": element.is_a(),
                "name": element.Name or "",
                "matrix": [float(v) for row in matrix for v in row],
                "container_name": container_name,
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
        return tool.Ifc.get() and tool.Spatial.get_active_container() and os.path.exists(clipboard_json)

    def _execute(self, context):
        clipboard_json = get_clipboard_path("bonsai_clipboard.json")
        clipboard_ifc = get_clipboard_path("bonsai_clipboard.ifc")
        
        with open(clipboard_json, "r") as f:
            clipboard_data = json.load(f)
        
        if clipboard_data.get("version") != 1:
            self.report({"ERROR"}, "Incompatible clipboard version")
            return {"CANCELLED"}
        
        if not os.path.exists(clipboard_ifc):
            self.report({"ERROR"}, "Clipboard library file not found")
            return {"CANCELLED"}
        
        ifc_file = tool.Ifc.get()
        
        library_file = ifcopenshell.open(clipboard_ifc)

        reuse_identities = {}
        pasted_elements = []
        pasted_objects = []
        
        # Show progress for large operations
        total = len(clipboard_data["elements"])
        show_progress = total > 20
        if show_progress:
            bpy.context.window_manager.progress_begin(0, 100)
        
        for i, elem_data in enumerate(clipboard_data["elements"]):
            if show_progress and i % max(1, total // 20) == 0:
                percent = int((i / total) * 100)
                bpy.context.window_manager.progress_update(percent)
            library_element = library_file.by_guid(elem_data["global_id"])
            
            copied_element = ifcopenshell.api.project.append_asset(
                ifc_file,
                library=library_file,
                element=library_element,
                reuse_identities=reuse_identities,  # Share identity map across all pastes
                assume_asset_uniqueness_by_name=False,  # Preserve distinct assets (as requested)
            )
            
            if not copied_element:
                self.report({"WARNING"}, f"Failed to copy {elem_data['ifc_class']}")
                continue
            
            matrix_data = elem_data["matrix"]
            matrix = Matrix([
                matrix_data[0:4],
                matrix_data[4:8],
                matrix_data[8:12],
                matrix_data[12:16]
            ])
            
            ifcopenshell.api.run(
                "geometry.edit_object_placement",
                ifc_file,
                product=copied_element,
                matrix=matrix,
                is_si=True
            )
            
            target_container = None
            if elem_data.get("container_name"):
                for container_candidate in ifc_file.by_type("IfcSpatialStructureElement"):
                    if container_candidate.Name == elem_data["container_name"]:
                        target_container = container_candidate
                        break
                
                if not target_container:
                    for source_container in library_file.by_type("IfcSpatialStructureElement"):
                        if source_container.Name == elem_data["container_name"]:
                            target_container = ifcopenshell.api.project.append_asset(
                                ifc_file,
                                library=library_file,
                                element=source_container,
                                reuse_identities=reuse_identities,  # Share identity map
                            )
                            if target_container:
                                logger = logging.getLogger("ImportIFC")
                                ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
                                container_importer = import_ifc.IfcImporter(ifc_import_settings)
                                container_importer.file = ifc_file
                                container_importer.process_context_filter()
                                
                                container_obj = container_importer.create_product(target_container)
                                if container_obj:
                                    tool.Collector.assign(container_obj)
                            break
            
            if target_container and tool.Spatial.can_contain(target_container, copied_element):
                ifcopenshell.api.run(
                    "spatial.assign_container",
                    ifc_file,
                    products=[copied_element],
                    relating_structure=target_container
                )
            
            pasted_elements.append(copied_element)
            
            logger = logging.getLogger("ImportIFC")
            ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
            ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
            ifc_importer.file = ifc_file
            ifc_importer.process_context_filter()
            ifc_importer.material_creator.load_existing_materials()
            
            elem_type = ifcopenshell.util.element.get_type(copied_element)
            if elem_type:
                if not tool.Ifc.get_object(elem_type):
                    self.import_materials(elem_type, ifc_importer)
                    self.import_styles(elem_type, ifc_importer)
                    ifc_importer.create_element_type(elem_type)
            
            self.import_materials(copied_element, ifc_importer)
            self.import_styles(copied_element, ifc_importer)
            ifc_importer.create_generic_elements({copied_element})
            ifc_importer.place_objects_in_collections()
            
            obj = tool.Ifc.get_object(copied_element)
            if obj:
                pasted_objects.append(obj)
        
        if pasted_objects:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in pasted_objects:
                obj.select_set(True)
            
            if pasted_objects:
                context.view_layer.objects.active = pasted_objects[0]
        
        ifc_file = tool.Ifc.get()
        if isinstance(ifc_file, ifcopenshell.sqlite):
            ifc_file.clear_cache()
        
        if show_progress:
            bpy.context.window_manager.progress_end()
        
        bonsai.bim.handler.refresh_ui_data()
        
        self.report({"INFO"}, f"Pasted {len(pasted_elements)} element(s)")
        return {"FINISHED"}
    
    def import_materials(self, element: ifcopenshell.entity_instance, ifc_importer) -> None:
        for material in ifcopenshell.util.element.get_materials(element):
            if tool.Ifc.get_object_by_identifier(material.id()):
                continue
            self.import_material_styles(material, ifc_importer)
    
    def import_styles(self, element: ifcopenshell.entity_instance, ifc_importer) -> None:
        ifc_file = tool.Ifc.get()
        if element.is_a("IfcTypeProduct"):
            representations = element.RepresentationMaps or []
        elif element.is_a("IfcProduct"):
            representations = [element.Representation] if element.Representation else []
        else:
            representations = []
        
        for representation in representations:
            for elem in ifc_file.traverse(representation):
                if not elem.is_a("IfcRepresentationItem") or not elem.StyledByItem:
                    continue
                for elem2 in ifc_file.traverse(elem.StyledByItem[0]):
                    if elem2.is_a("IfcSurfaceStyle") and not tool.Ifc.get_object_by_identifier(elem2.id()):
                        ifc_importer.create_style(elem2)
    
    def import_material_styles(self, material: ifcopenshell.entity_instance, ifc_importer) -> None:
        ifc_file = tool.Ifc.get()
        if not material.HasRepresentation:
            return
        for elem in ifc_file.traverse(material.HasRepresentation[0]):
            if elem.is_a("IfcSurfaceStyle") and not tool.Ifc.get_object_by_identifier(elem.id()):
                ifc_importer.create_style(elem)





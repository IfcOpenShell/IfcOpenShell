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
import bonsai
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.selector
import ifcopenshell.api.project
import ifcopenshell.guid
from ifcopenshell.util.element import copy_deep
from mathutils import Matrix
from bonsai.bim.ifc import IfcStore
import bonsai.tool as tool
import bonsai.bim.import_ifc as import_ifc
import bonsai.bim.handler


def get_clipboard_path(filename):
    return tool.Blender.get_data_dir_path(filename).__str__()


class BonsaiGraphClipboardEngine:
    """
    Graph-safe IFC clipboard paste engine.

    Usage:
        engine = BonsaiGraphClipboardEngine(target_ifc)
        new_elements = engine.paste_from_file(
            clipboard_ifc_path,
            clipboard_json_data,
            context
        )
    """

    UNSAFE_CLASSES = {
        "IfcProject",
        "IfcSite",
        "IfcBuilding",
        "IfcBuildingStorey",
        "IfcGeometricRepresentationContext",
        "IfcUnitAssignment",
    }

    def __init__(self, target_model: ifcopenshell.file):
        self.target = target_model

    def paste_from_file(self, clipboard_ifc_path, clipboard_data, context, paste_mode="DUPLICATE"):
        """
        Main entry point.

        :param clipboard_ifc_path: path to clipboard.ifc
        :param clipboard_data: loaded JSON metadata
        :param context: Blender context
        :param paste_mode: How to handle name conflicts (DUPLICATE, RENAME, DESTINATION, SOURCE)
        :return: list of newly created IfcProduct elements
        """

        source = ifcopenshell.open(clipboard_ifc_path)

        roots = self._collect_safe_roots(source, clipboard_data)

        if not roots:
            return []

        # Show progress for large operations
        total = len(roots)
        show_progress = total > 20
        if show_progress:
            bpy.context.window_manager.progress_begin(0, 100)
            bpy.context.window_manager.progress_update(1)

        new_elements = self._clone_graph(source, roots, show_progress, paste_mode)

        if show_progress:
            bpy.context.window_manager.progress_update(85)

        self._reattach_to_active_container(new_elements, context)

        if show_progress:
            bpy.context.window_manager.progress_update(90)

        self._import_into_blender(new_elements)

        if show_progress:
            bpy.context.window_manager.progress_update(100)
            bpy.context.window_manager.progress_end()

        return new_elements


    def _collect_safe_roots(self, source, clipboard_data):

        roots = []

        for elem_data in clipboard_data.get("elements", []):
            guid = elem_data.get("global_id")
            if not guid:
                continue

            try:
                element = source.by_guid(guid)
            except RuntimeError:
                continue

            if element.is_a() not in self.UNSAFE_CLASSES:
                roots.append(element)

        return roots

    # --------------------------------------------------------
    
    def _build_context_map(self, source, copied_entities, original_context_ids):

        context_map = {}
        
        # Get target file's original contexts (these existed before paste)
        original_contexts = [ctx for ctx in self.target.by_type("IfcGeometricRepresentationContext") 
                            if ctx.id() in original_context_ids]
        
        # Build a quick lookup for original contexts by their signature
        original_context_lookup = {}
        for context in original_contexts:
            if context.is_a("IfcGeometricRepresentationSubcontext"):
                parent = context.ParentContext
                key = (context.ContextType, context.ContextIdentifier, context.TargetView, 
                       parent.ContextType if parent else None)
            else:
                key = (context.ContextType, None, None, None)
            original_context_lookup[key] = context
        
        # Map copied contexts to original contexts
        # Any context not in original_context_ids was copied and needs to be mapped
        for entity in self.target.by_type("IfcGeometricRepresentationContext"):
            if entity.id() in original_context_ids:
                continue  # This is an original context, skip it
            
            # This is a copied context - map it to the original
            if entity.is_a("IfcGeometricRepresentationSubcontext"):
                parent = entity.ParentContext
                key = (entity.ContextType, entity.ContextIdentifier, entity.TargetView,
                       parent.ContextType if parent else None)
            else:
                key = (entity.ContextType, None, None, None)
            
            if key in original_context_lookup:
                # Map copied context ID -> original context
                context_map[entity.id()] = original_context_lookup[key]
        
        return context_map
    
    def _remap_representation_contexts(self, element, context_map):
        """
        Remap representation contexts for an element to use target file's contexts.
        """
        # Handle regular products with Representation
        try:
            if element.Representation:
                for rep in element.Representation.Representations:
                    self._remap_single_representation(rep, context_map)
        except AttributeError:
            pass
        
        # Handle type products with RepresentationMaps
        try:
            if element.RepresentationMaps:
                for rep_map in element.RepresentationMaps:
                    if rep_map.MappedRepresentation:
                        self._remap_single_representation(rep_map.MappedRepresentation, context_map)
        except AttributeError:
            pass
    
    def _remap_single_representation(self, rep, context_map):
        """
        Remap a single representation's context.
        """
        if not rep.ContextOfItems:
            return
        
        current_context = rep.ContextOfItems
        
        # Check if this context is in our map (i.e., it was copied and needs to be replaced)
        if current_context.id() in context_map:
            rep.ContextOfItems = context_map[current_context.id()]
            return
        
        # Fallback: try to find a matching context by signature
        # This handles cases where the context wasn't in copied_entities
        if current_context.is_a("IfcGeometricRepresentationSubcontext"):
            parent = current_context.ParentContext
            for target_ctx in self.target.by_type("IfcGeometricRepresentationSubcontext"):
                if (target_ctx.ContextType == current_context.ContextType and
                    target_ctx.ContextIdentifier == current_context.ContextIdentifier and
                    target_ctx.TargetView == current_context.TargetView and
                    target_ctx.ParentContext.ContextType == (parent.ContextType if parent else None)):
                    # Found a match in the target file's original contexts
                    rep.ContextOfItems = target_ctx
                    return
        else:
            # Main context (not a subcontext)
            for target_ctx in self.target.by_type("IfcGeometricRepresentationContext"):
                if (not target_ctx.is_a("IfcGeometricRepresentationSubcontext") and
                    target_ctx.ContextType == current_context.ContextType):
                    rep.ContextOfItems = target_ctx
                    return

    # --------------------------------------------------------
    
    def _build_existing_elements_map(self, existing_by_name):
        """
        Build a map of existing elements in target file by name and type.
        Used for DESTINATION mode to reuse existing elements.
        
        :param existing_by_name: Dictionary to populate with {(class, name): element}
        """
        import logging
        logger = logging.getLogger("BIM")
        print("\n=== Building existing elements map for DESTINATION mode ===")
        logger.info("=== Building existing elements map for DESTINATION mode ===")
        
        # Map type products by (class, Name) - these can be reused
        for product in self.target.by_type("IfcTypeProduct"):
            try:
                if hasattr(product, "Name") and product.Name is not None:
                    key = (product.is_a(), product.Name)
                    existing_by_name[key] = product
                    print(f"  Existing TYPE: {product.is_a()} '{product.Name}' (id={product.id()})")
            except:
                pass
        
        # Map materials by ("IfcMaterial", Name)
        for material in self.target.by_type("IfcMaterial"):
            try:
                if hasattr(material, "Name") and material.Name is not None:
                    key = ("IfcMaterial", material.Name)
                    existing_by_name[key] = material
                    print(f"  Existing: IfcMaterial '{material.Name}' (id={material.id()})")
                    logger.info(f"  Existing: IfcMaterial '{material.Name}' (id={material.id()})")
            except:
                pass
        
        # Map profiles by (class, ProfileName)
        for profile in self.target.by_type("IfcProfileDef"):
            try:
                if hasattr(profile, "ProfileName") and profile.ProfileName is not None:
                    key = (profile.is_a(), profile.ProfileName)
                    existing_by_name[key] = profile
                    print(f"  Existing: {profile.is_a()} '{profile.ProfileName}' (id={profile.id()})")
                    logger.info(f"  Existing: {profile.is_a()} '{profile.ProfileName}' (id={profile.id()})")
            except:
                pass
        
        # Map styles by (class, Name)
        for style in self.target.by_type("IfcPresentationStyle"):
            try:
                if hasattr(style, "Name") and style.Name is not None:
                    key = (style.is_a(), style.Name)
                    existing_by_name[key] = style
                    print(f"  Existing: {style.is_a()} '{style.Name}' (id={style.id()})")
                    logger.info(f"  Existing: {style.is_a()} '{style.Name}' (id={style.id()})")
            except:
                pass
        
        print(f"=== Found {len(existing_by_name)} existing elements ===")
        logger.info(f"=== Found {len(existing_by_name)} existing elements ===")
    
    def _find_existing_element(self, source_element, existing_by_name, paste_mode):
        """
        Find an existing element in the target file that matches the source element.
        Used for DESTINATION mode.
        
        :param source_element: Element from source file
        :param existing_by_name: Map of existing elements
        :param paste_mode: Current paste mode
        :return: Existing element if found and mode is DESTINATION, None otherwise
        """
        if paste_mode != "DESTINATION":
            return None
        
        try:
            ifc_class = source_element.is_a()
            
            # Check for products AND types by Name
            # Note: is_a("IfcProduct") may return False for types from source file due to cross-file inheritance issues
            # So we explicitly check both IfcProduct and IfcTypeProduct
            is_product_or_type = source_element.is_a("IfcProduct") or source_element.is_a("IfcTypeProduct")
            if is_product_or_type:
                if hasattr(source_element, "Name") and source_element.Name is not None:
                    key = (ifc_class, source_element.Name)
                    result = existing_by_name.get(key)
                    return result
            
            # Check for materials by Name
            elif source_element.is_a("IfcMaterial"):
                if hasattr(source_element, "Name") and source_element.Name is not None:
                    key = ("IfcMaterial", source_element.Name)
                    return existing_by_name.get(key)
            
            # Check for profiles by ProfileName
            elif source_element.is_a("IfcProfileDef"):
                if hasattr(source_element, "ProfileName") and source_element.ProfileName is not None:
                    key = (ifc_class, source_element.ProfileName)
                    return existing_by_name.get(key)
            
            # Check for styles by Name
            elif source_element.is_a("IfcPresentationStyle"):
                if hasattr(source_element, "Name") and source_element.Name is not None:
                    key = (ifc_class, source_element.Name)
                    return existing_by_name.get(key)
        except Exception as e:
            pass
        
        return None
    
    def _prepopulate_copied_entities(self, source, root_elements, copied_entities, existing_by_name, paste_mode):
        """
        Pre-scan source elements and populate copied_entities with existing destination elements.
        This ensures copy_deep reuses existing materials, styles, profiles, and types.
        
        :param source: Source IFC file
        :param root_elements: Elements being copied
        :param copied_entities: Dictionary to populate with source_id -> destination_element
        :param existing_by_name: Map of existing elements in destination
        :param paste_mode: Current paste mode (should be DESTINATION)
        """
        import logging
        logger = logging.getLogger("BIM")
        print(f"\n=== Pre-populating copied_entities for {paste_mode} mode ===")
        logger.info(f"=== Pre-populating copied_entities for {paste_mode} mode ===")
        
        # Collect all materials, styles, profiles, types referenced by elements
        # We need to use the same logic as _clone_graph to find dependencies
        elements_to_check = set()
        
        for root in root_elements:
            # Get the element type
            element_type = ifcopenshell.util.element.get_type(root)
            if element_type:
                elements_to_check.add(element_type)
                print(f"  Found type: {element_type.is_a()} '{element_type.Name}' for {root.is_a()} '{root.Name}'")
                
                # Get type's materials
                type_material = ifcopenshell.util.element.get_material(element_type)
                if type_material:
                    elements_to_check.add(type_material)
                    mat_name = getattr(type_material, 'Name', None) or '(unnamed)'
                    print(f"    Found type material: {type_material.is_a()} '{mat_name}'")
                
                # Get all materials from type
                try:
                    type_materials_list = ifcopenshell.util.element.get_materials(element_type)
                    for mat in type_materials_list:
                        elements_to_check.add(mat)
                        # Also check for styled representations
                        for material_rep in getattr(mat, 'HasRepresentation', []):
                            for rep in getattr(material_rep, 'Representations', []):
                                for item in getattr(rep, 'Items', []):
                                    for styled_item in getattr(item, 'Styles', []):
                                        elements_to_check.add(styled_item)
                except:
                    pass
            
            # Get occurrence materials
            occurrence_material = ifcopenshell.util.element.get_material(root)
            if occurrence_material:
                elements_to_check.add(occurrence_material)
                mat_name = getattr(occurrence_material, 'Name', None) or '(unnamed)'
                print(f"  Found occurrence material: {occurrence_material.is_a()} '{mat_name}' for {root.is_a()} '{root.Name}'")
            
            # Get all materials (handles material sets, layers, etc.)
            try:
                materials_list = ifcopenshell.util.element.get_materials(root)
                for mat in materials_list:
                    elements_to_check.add(mat)
                    # Check for styled representations of materials
                    for material_rep in getattr(mat, 'HasRepresentation', []):
                        for rep in getattr(material_rep, 'Representations', []):
                            for item in getattr(rep, 'Items', []):
                                for styled_item in getattr(item, 'Styles', []):
                                    elements_to_check.add(styled_item)
            except:
                pass
            
            # Also traverse for geometric dependencies (profiles, etc.)
            for element in source.traverse(root):
                elements_to_check.add(element)
        
        print(f"Checking {len(elements_to_check)} source elements for potential reuse")
        logger.info(f"  Checking {len(elements_to_check)} source elements")
        
        # Check each element and map to existing destination element if found
        reused_count = 0
        checked_count = 0
        for element in elements_to_check:
            try:
                # Skip if already mapped
                if element.id() in copied_entities:
                    continue
                
                # Skip product instances (they always need new GUIDs)
                # But allow types, materials, profiles, styles to be reused
                if element.is_a("IfcProduct") and not element.is_a("IfcTypeProduct"):
                    continue
                
                # Log what we're checking (types, materials, styles, profiles)
                checked_count += 1
                elem_name = ""
                if hasattr(element, "Name"):
                    elem_name = element.Name or "(no name)"
                elif hasattr(element, "ProfileName"):
                    elem_name = element.ProfileName or "(no name)"
                else:
                    elem_name = "(no name attr)"
                
                # Highlight materials, styles, types for easier debugging
                if element.is_a("IfcMaterial") or element.is_a("IfcTypeProduct") or element.is_a("IfcPresentationStyle") or element.is_a("IfcProfileDef"):
                    print(f"  Checking: {element.is_a()} '{elem_name}' (source_id={element.id()})")
                
                # Try to find existing match
                existing = self._find_existing_element(element, existing_by_name, paste_mode)
                if existing:
                    # Map source ID to destination element
                    copied_entities[element.id()] = existing
                    reused_count += 1
                    
                    # Log what we're reusing
                    elem_name = ""
                    if hasattr(element, "Name"):
                        elem_name = element.Name or ""
                    elif hasattr(element, "ProfileName"):
                        elem_name = element.ProfileName or ""
                    print(f"  REUSE: {element.is_a()} '{elem_name}' source_id={element.id()} -> dest_id={existing.id()}")
                    logger.info(f"  REUSE: {element.is_a()} '{elem_name}' source_id={element.id()} -> dest_id={existing.id()}")
            except Exception as e:
                logger.warning(f"  Error checking element: {e}")
                pass
        
        print(f"Checked {checked_count} elements (skipped product instances)")
        print(f"=== Pre-populated {reused_count} elements for reuse ===")
        logger.info(f"=== Pre-populated {reused_count} elements for reuse ===")

    # --------------------------------------------------------

    def _clone_graph(self, source, root_elements, show_progress=False, paste_mode="DUPLICATE"):
        """
        Clone subgraph safely into target model.
        Regenerates all IfcRoot GUIDs.
        
        :param source: Source IFC file
        :param root_elements: List of root elements to copy
        :param show_progress: Whether to show progress indicator
        :param paste_mode: How to handle name conflicts (DUPLICATE, RENAME, DESTINATION, SOURCE)
        """
        import logging
        logger = logging.getLogger("BIM")
        print(f"\n=== PASTE OPERATION START ===")
        print(f"Mode: {paste_mode}")
        print(f"Elements to paste: {len(root_elements)}")
        logger.info(f"=== Starting paste with mode: {paste_mode} ===")
        logger.info(f"  Pasting {len(root_elements)} root elements")
        
        # Record existing contexts before copying anything
        # These are the "original" contexts we want to use
        original_context_ids = {ctx.id() for ctx in self.target.by_type("IfcGeometricRepresentationContext")}

        copied_entities = {}  # Reuse map for shared dependencies
        guid_map = {}
        
        # For DESTINATION mode, build lookup of existing elements by name
        # and pre-populate copied_entities with them so copy_deep reuses them
        # For SOURCE mode, skip this - we don't want to reuse destination elements,
        # just deduplicate within the paste operation itself (handled by copy_deep)
        existing_by_name = {}
        if paste_mode == "DESTINATION":
            self._build_existing_elements_map(existing_by_name)
            # Pre-scan source elements and map them to existing destination elements
            self._prepopulate_copied_entities(source, root_elements, copied_entities, existing_by_name, paste_mode)

        # Precompute GUID remapping for entire subtree
        for root in root_elements:
            for element in source.traverse(root):
                if element.is_a("IfcRoot"):
                    if element.GlobalId not in guid_map:
                        guid_map[element.GlobalId] = ifcopenshell.guid.new()

        # First, copy all materials, styles, types, and property sets referenced by elements
        # This ensures they're in the reuse map before copying elements
        element_types = {}  # Track element -> type mapping for reconnection later
        type_materials = {}  # Track type -> material mapping for reconnection
        element_psets = {}  # Track element -> property sets mapping for reconnection
        type_psets = {}  # Track type -> property sets mapping for reconnection
        
        # Progress: 1-10% for dependency copying
        for idx, root in enumerate(root_elements):
            if show_progress and idx % max(1, len(root_elements) // 20) == 0:
                progress = 1 + int(9 * idx / len(root_elements))
                bpy.context.window_manager.progress_update(progress)
            
            # Copy the element type if it exists
            element_type = ifcopenshell.util.element.get_type(root)
            if element_type:
                if element_type.id() not in copied_entities:
                    # Will use copied_entities for reuse (pre-populated in DESTINATION mode)
                    print(f"Copying type {element_type.is_a()} '{element_type.Name}' (source_id={element_type.id()})")
                    copied_type = copy_deep(
                        self.target, 
                        element_type, 
                        copied_entities=copied_entities,
                    )
                    element_types[root.id()] = copied_type
                    print(f"  -> Created new type dest_id={copied_type.id()}")
                else:
                    # Type was pre-populated (reused from destination)
                    existing_type = copied_entities[element_type.id()]
                    element_types[root.id()] = existing_type
                    
                # Copy the type's material (types can have materials separate from occurrences)
                type_material = ifcopenshell.util.element.get_material(element_type)
                if type_material and type_material.id() not in copied_entities:
                    copy_deep(self.target, type_material, copied_entities=copied_entities)
                
                # Copy type material's styled representations
                type_materials_list = ifcopenshell.util.element.get_materials(element_type)
                for mat in type_materials_list:
                    for material_rep in getattr(mat, 'HasRepresentation', []):
                        if material_rep.id() not in copied_entities:
                            copy_deep(self.target, material_rep, copied_entities=copied_entities)
                
                # Track the type's material associations for reconnection
                for association in getattr(element_type, 'HasAssociations', []):
                    if association.is_a('IfcRelAssociatesMaterial'):
                        type_materials[element_type.id()] = association.RelatingMaterial
                
                # Copy and track the type's property sets
                type_psets_list = []
                for rel in getattr(element_type, 'IsDefinedBy', []):
                    if rel.is_a('IfcRelDefinesByProperties'):
                        pset = rel.RelatingPropertyDefinition
                        if pset.id() not in copied_entities:
                            copied_pset = copy_deep(self.target, pset, copied_entities=copied_entities)
                            type_psets_list.append(copied_pset)
                        else:
                            type_psets_list.append(copied_entities[pset.id()])
                
                if type_psets_list:
                    type_psets[element_type.id()] = type_psets_list
            
            # Get materials and copy them along with their styles
            # Materials will be reused from copied_entities if in DESTINATION mode
            material = ifcopenshell.util.element.get_material(root)
            if material:
                if material.id() not in copied_entities:
                    copy_deep(self.target, material, copied_entities=copied_entities)
            
            # Get individual materials (handles material sets) and copy their representations
            materials = ifcopenshell.util.element.get_materials(root)
            for mat in materials:
                # Copy material definition representations (which contain styled items and styles)
                for material_rep in getattr(mat, 'HasRepresentation', []):
                    if material_rep.id() not in copied_entities:
                        # This will recursively copy the representation, styled items, and styles
                        copy_deep(self.target, material_rep, copied_entities=copied_entities)
            
            # Get styles from representation items (styled items)
            try:
                if root.Representation:
                    for rep in root.Representation.Representations:
                        for item in rep.Items:
                            # Copy any styled items that style this representation item
                            for styled_item in getattr(item, 'StyledByItem', []):
                                if styled_item.id() not in copied_entities:
                                    # This will recursively copy the styled item and its referenced styles
                                    copy_deep(self.target, styled_item, copied_entities=copied_entities)
            except AttributeError:
                pass
            
            # Copy property sets and quantities
            psets_for_element = []
            for rel in getattr(root, 'IsDefinedBy', []):
                if rel.is_a('IfcRelDefinesByProperties'):
                    pset = rel.RelatingPropertyDefinition
                    if pset.id() not in copied_entities:
                        # Copy the property set (will recursively copy all properties)
                        copied_pset = copy_deep(self.target, pset, copied_entities=copied_entities)
                        psets_for_element.append(copied_pset)
                    else:
                        psets_for_element.append(copied_entities[pset.id()])
            
            if psets_for_element:
                element_psets[root.id()] = psets_for_element

        new_roots = []
        
        # Collect reconnection data to process in batches after all copying is complete
        # This avoids thousands of API calls with large copied_entities dictionaries
        type_reconnections = []  # (new_root, copied_type)
        type_material_reconnections = []  # (copied_type, copied_material)
        type_pset_reconnections = []  # (copied_type, pset)
        material_reconnections = []  # (new_root, copied_material)
        pset_reconnections = []  # (new_root, pset)

        # Progress: 10-70% for element copying (most expensive operation)
        for idx, root in enumerate(root_elements):
            if show_progress and idx % max(1, len(root_elements) // 40) == 0:
                progress = 10 + int(60 * idx / len(root_elements))
                bpy.context.window_manager.progress_update(progress)
            
            # Log what we're copying
            try:
                element_name = getattr(root, "Name", None) or "(unnamed)"
                print(f"Copying [{idx+1}/{len(root_elements)}]: {root.is_a()} '{element_name}' (source_id={root.id()})")
                if root.id() in copied_entities:
                    print(f"  -> PRE-MAPPED to dest_id={copied_entities[root.id()].id()}")
            except:
                pass
            
            new_root = copy_deep(
                self.target,
                root,
                copied_entities=copied_entities,
            )
            
            # Check if type was already assigned by copy_deep
            try:
                print(f"  -> Result: dest_id={new_root.id()}")
                existing_type = ifcopenshell.util.element.get_type(new_root)
                if existing_type:
                    print(f"  -> copy_deep already assigned type: {existing_type.is_a()} '{existing_type.Name}' (id={existing_type.id()})")
                else:
                    print(f"  -> copy_deep did NOT assign a type")
            except Exception as e:
                print(f"  -> Error checking type: {e}")
            
            # Collect reconnection data instead of calling API immediately
            if root.id() in element_types:
                copied_type = element_types[root.id()]
                # Only reconnect if copy_deep didn't already assign the type
                try:
                    existing_type_after_copy = ifcopenshell.util.element.get_type(new_root)
                    if existing_type_after_copy:
                        print(f"  -> Skipping type reconnection (already has type id={existing_type_after_copy.id()})")
                    else:
                        print(f"  -> Will reconnect type {copied_type.is_a()} (id={copied_type.id()})")
                        type_reconnections.append((new_root, copied_type))
                except Exception as e:
                    print(f"  -> Error during type reconnection check: {e}")
                    # If error checking, assume we need to reconnect
                    type_reconnections.append((new_root, copied_type))
                
                # Collect type's material associations
                original_type = ifcopenshell.util.element.get_type(root)
                if original_type and original_type.id() in type_materials:
                    type_material = type_materials[original_type.id()]
                    if type_material.id() in copied_entities:
                        copied_type_material = copied_entities[type_material.id()]
                        type_material_reconnections.append((copied_type, copied_type_material))
                
                # Collect type's property sets
                if original_type and original_type.id() in type_psets:
                    for pset in type_psets[original_type.id()]:
                        type_pset_reconnections.append((copied_type, pset))
            
            # Collect material associations
            for association in getattr(root, 'HasAssociations', []):
                if association.is_a('IfcRelAssociatesMaterial'):
                    material = association.RelatingMaterial
                    if material.id() in copied_entities:
                        copied_material = copied_entities[material.id()]
                        material_reconnections.append((new_root, copied_material))
            
            # Collect property sets
            if root.id() in element_psets:
                for pset in element_psets[root.id()]:
                    pset_reconnections.append((new_root, pset))

            # Apply GUID remapping
            for element in self.target.traverse(new_root):
                if element.is_a("IfcRoot"):
                    old_guid = element.GlobalId
                    if old_guid in guid_map:
                        element.GlobalId = guid_map[old_guid]

            new_roots.append(new_root)
        
        # Now process all reconnections in batches using API calls
        # This is much faster than calling API during the loop with large copied_entities dictionaries
        
        # Progress: 70-72% for type reconnections
        if show_progress:
            bpy.context.window_manager.progress_update(70)
        
        # Reconnect types
        if type_reconnections:
            print(f"\n=== Reconnecting {len(type_reconnections)} type relationships ===")
            for new_root, copied_type in type_reconnections:
                try:
                    # Check if the product already has this type assigned
                    current_type = ifcopenshell.util.element.get_type(new_root)
                    if current_type and current_type.id() == copied_type.id():
                        print(f"Product {new_root.is_a()} '{new_root.Name}' (id={new_root.id()}) already has type {copied_type.is_a()} (id={copied_type.id()}) - skipping")
                        continue
                    
                    print(f"Assigning type {copied_type.is_a()} '{copied_type.Name}' (id={copied_type.id()}) to {new_root.is_a()} '{new_root.Name}' (id={new_root.id()})")
                    ifcopenshell.api.run(
                        "type.assign_type",
                        self.target,
                        should_run_listeners=False,
                        related_objects=[new_root],
                        relating_type=copied_type,
                    )
                    # Verify it worked
                    assigned_type = ifcopenshell.util.element.get_type(new_root)
                    print(f"  -> Assigned type id={assigned_type.id() if assigned_type else 'None'}")
                except Exception as e:
                    print(f"  -> ERROR: {e}")
        
        # Progress: 72-74% for type materials
        if show_progress:
            bpy.context.window_manager.progress_update(72)
        
        # Reconnect type materials
        if type_material_reconnections:
            # Group by material to reduce API calls
            type_material_groups = {}
            for copied_type, copied_material in type_material_reconnections:
                if copied_material.id() not in type_material_groups:
                    type_material_groups[copied_material.id()] = []
                type_material_groups[copied_material.id()].append(copied_type)
            
            # Assign in batches
            for material_id, products in type_material_groups.items():
                copied_material = self.target.by_id(material_id)
                ifcopenshell.api.run(
                    "material.assign_material",
                    self.target,
                    should_run_listeners=False,
                    products=products,  # Batch assignment
                    material=copied_material,
                )
        
        # Progress: 74-76% for type psets
        if show_progress:
            bpy.context.window_manager.progress_update(74)
        
        # Reconnect type psets
        if type_pset_reconnections:
            # Group by pset to reduce API calls
            type_pset_groups = {}
            for copied_type, pset in type_pset_reconnections:
                if pset.id() not in type_pset_groups:
                    type_pset_groups[pset.id()] = []
                type_pset_groups[pset.id()].append(copied_type)
            
            # Assign in batches
            for pset_id, products in type_pset_groups.items():
                pset = self.target.by_id(pset_id)
                ifcopenshell.api.run(
                    "pset.assign_pset",
                    self.target,
                    should_run_listeners=False,
                    products=products,  # Batch assignment
                    pset=pset,
                )
        
        # Progress: 76-78% for materials
        if show_progress:
            bpy.context.window_manager.progress_update(76)
        
        # Reconnect materials
        if material_reconnections:
            # Group by material to reduce API calls
            material_groups = {}
            for new_root, copied_material in material_reconnections:
                if copied_material.id() not in material_groups:
                    material_groups[copied_material.id()] = []
                material_groups[copied_material.id()].append(new_root)
            
            # Assign in batches
            for material_id, products in material_groups.items():
                copied_material = self.target.by_id(material_id)
                ifcopenshell.api.run(
                    "material.assign_material",
                    self.target,
                    should_run_listeners=False,
                    products=products,  # Batch assignment
                    material=copied_material,
                )
        
        # Progress: 78-80% for psets
        if show_progress:
            bpy.context.window_manager.progress_update(78)
        
        # Reconnect psets
        if pset_reconnections:
            # Group by pset to reduce API calls
            pset_groups = {}
            for new_root, pset in pset_reconnections:
                if pset.id() not in pset_groups:
                    pset_groups[pset.id()] = []
                pset_groups[pset.id()].append(new_root)
            
            # Assign in batches
            for pset_id, products in pset_groups.items():
                pset = self.target.by_id(pset_id)
                ifcopenshell.api.run(
                    "pset.assign_pset",
                    self.target,
                    should_run_listeners=False,
                    products=products,  # Batch assignment
                    pset=pset,
                )
        
        # Progress: 80% for array GUID updates
        if show_progress:
            bpy.context.window_manager.progress_update(80)
        
        # Update array child GUIDs (arrays store child element GUIDs which were regenerated during copy)
        # Build reverse lookup: old GUID -> new GUID
        old_guid_to_new_guid = {}
        for old_entity_id, new_entity in copied_entities.items():
            try:
                old_entity = source.by_id(old_entity_id)
                if old_entity.is_a("IfcRoot"):  # Only IfcRoot entities have GlobalId
                    old_guid_to_new_guid[old_entity.GlobalId] = new_entity.GlobalId
            except:
                pass
        
        # Update all BBIM_Array psets to use new child GUIDs
        for element in self.target.by_type("IfcRoot"):
            array_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            if array_pset and "Data" in array_pset and array_pset["Data"]:
                try:
                    data = json.loads(array_pset["Data"])
                    updated = False
                    for array in data:
                        if "children" in array:
                            new_children = []
                            for old_child_guid in array["children"]:
                                new_guid = old_guid_to_new_guid.get(old_child_guid, old_child_guid)
                                new_children.append(new_guid)
                            if new_children != array["children"]:
                                array["children"] = new_children
                                updated = True
                    
                    if updated:
                        pset_entity = self.target.by_id(array_pset["id"])
                        new_data = self.target.createIfcText(json.dumps(data))
                        ifcopenshell.api.run(
                            "pset.edit_pset",
                            self.target,
                            should_run_listeners=False,
                            pset=pset_entity,
                            properties={"Data": new_data}
                        )
                except:
                    pass
        
        # Progress: 81% for context remapping
        if show_progress:
            bpy.context.window_manager.progress_update(81)
        
        # After all copying is done, remap representation contexts to use target file's contexts
        # This prevents duplicate contexts and ensures proper representation management
        context_map = self._build_context_map(source, copied_entities, original_context_ids)
        
        # Remap contexts for all copied types
        for copied_type in element_types.values():
            self._remap_representation_contexts(copied_type, context_map)
        
        # Remap contexts for all copied roots
        for new_root in new_roots:
            self._remap_representation_contexts(new_root, context_map)
        
        # Remap contexts for material definition representations
        # These also have representations with context references
        for mat_def_rep in self.target.by_type("IfcMaterialDefinitionRepresentation"):
            # Only process if this was in our copied set (check by checking if it has remapped context)
            if mat_def_rep.Representations:
                for rep in mat_def_rep.Representations:
                    if rep.ContextOfItems and rep.ContextOfItems.id() in context_map:
                        self._remap_single_representation(rep, context_map)
        
        # Progress: 83% for context cleanup
        if show_progress:
            bpy.context.window_manager.progress_update(83)
        
        # Remove duplicate contexts that were copied (they're no longer needed after remapping)
        # Remove subcontexts first, then parent contexts to avoid referential integrity issues
        # We do this carefully to avoid crashes with large pastes
        duplicate_context_ids = set(context_map.keys())
        
        # Build reverse lookup: which contexts are still being used
        contexts_in_use = set()
        for rep in self.target.by_type("IfcRepresentation"):
            if rep.ContextOfItems:
                contexts_in_use.add(rep.ContextOfItems.id())
        
        # Only remove contexts that are definitely not in use
        removed_count = 0
        for ctx_id in duplicate_context_ids:
            if ctx_id not in contexts_in_use:
                ctx = self.target.by_id(ctx_id)
                if ctx:
                    # For parent contexts, check if they have any remaining subcontexts
                    if ctx.is_a("IfcGeometricRepresentationSubcontext"):
                        try:
                            self.target.remove(ctx)
                            removed_count += 1
                        except:
                            pass
                    else:
                        # Check if this parent has any subcontexts still in use
                        has_subcontexts = False
                        for subctx in self.target.by_type("IfcGeometricRepresentationSubcontext"):
                            if subctx.ParentContext and subctx.ParentContext.id() == ctx.id():
                                has_subcontexts = True
                                break
                        if not has_subcontexts:
                            try:
                                self.target.remove(ctx)
                                removed_count += 1
                            except:
                                pass
        
# Progress: 84% complete
        if show_progress:
            bpy.context.window_manager.progress_update(84)

        return new_roots

    # --------------------------------------------------------

    def _reattach_to_active_container(self, new_elements, context):
        """
        Attach pasted elements to active spatial container.
        Does not import old containment relationships.
        """

        active_container = tool.Spatial.get_active_container()
        
        # Validate that the container is a proper spatial structure (not IfcProject)
        if active_container and not active_container.is_a("IfcSpatialStructureElement"):
            active_container = None

        if not active_container:
            # Try to find any building storey
            storeys = self.target.by_type("IfcBuildingStorey")
            if storeys:
                active_container = storeys[0]
            else:
                # Try building, then site as fallback
                buildings = self.target.by_type("IfcBuilding")
                if buildings:
                    active_container = buildings[0]
                else:
                    sites = self.target.by_type("IfcSite")
                    if sites:
                        active_container = sites[0]

        if not active_container:
            return

        for element in new_elements:
            self.target.create_entity(
                "IfcRelContainedInSpatialStructure",
                GlobalId=ifcopenshell.guid.new(),
                RelatingStructure=active_container,
                RelatedElements=[element],
            )

    # --------------------------------------------------------

    def _import_into_blender(self, new_elements):
        """
        Create Blender objects for new IFC products.
        """
        
        if not new_elements:
            return
        
        try:
            # Create importer with factory settings
            ifc_import_settings = import_ifc.IfcImportSettings.factory()
            ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
            
            # Set up importer for the target file
            ifc_importer.file = self.target
            ifc_importer.calculate_unit_scale()
            ifc_importer.process_context_filter()
            
            # Load any existing materials first (for reuse)
            ifc_importer.material_creator.load_existing_materials()
            
            # Create Blender materials/styles from IFC styles
            ifc_importer.create_styles()
            
            # Collect element types from the pasted products
            element_types = set()
            for element in new_elements:
                if element.is_a("IfcProduct"):
                    element_type = ifcopenshell.util.element.get_type(element)
                    if element_type:
                        # Only import types that don't already have Blender objects
                        # (reused types from DESTINATION mode already have objects)
                        if not tool.Ifc.get_object(element_type):
                            element_types.add(element_type)
            
            # Import element types first
            if element_types:
                ifc_importer.element_types = element_types
                ifc_importer.create_element_types()
            
            # Import all products
            products = set(e for e in new_elements if e.is_a("IfcProduct"))
            if products:
                ifc_importer.create_generic_elements(products)
                ifc_importer.setup_arrays()
                
                # Assign all created objects to their collections (filter out materials)
                for obj in ifc_importer.added_data.values():
                    if isinstance(obj, bpy.types.Object):
                        try:
                            tool.Collector.assign(obj, should_clean_users_collection=False)
                        except Exception as e:
                            import logging
                            logging.getLogger("BIM").warning(f"Failed to assign object {obj.name} to collection: {e}")
                            
        except Exception as e:
            import logging
            logging.getLogger("BIM").exception("Error during Blender import")
            raise

    # --------------------------------------------------------

    def copy_to_file(self, source_file, elements, output_path, show_progress=False):
        """
        Extract elements into a clipboard IFC file.

        :param source_file: Source IFC file
        :param elements: List of elements to copy
        :param output_path: Path to write clipboard.ifc
        :param show_progress: Whether to show progress updates
        :return: New IFC file with extracted elements
        """

        clipboard = ifcopenshell.file(schema_version=source_file.schema_version)
        reuse_map = {}
        owner_history = None

        # Copy owner history
        for oh in source_file.by_type("IfcOwnerHistory"):
            owner_history = clipboard.add(oh)
            break

        # Copy project
        project = source_file.by_type("IfcProject")[0]
        clipboard.add(project)

        # Track spatial relationships for reconstruction
        contained_ins = {}  # {container_guid: set(elements)}
        aggregates = {}  # {parent_guid: set(children)}

        def append_asset(element):
            """Add element to clipboard, reusing if already added."""
            if element.is_a("IfcProject"):
                return clipboard.by_type("IfcProject")[0]

            return ifcopenshell.api.project.append_asset(
                clipboard,
                library=source_file,
                element=element,
                reuse_identities=reuse_map,
                assume_asset_uniqueness_by_name=False,
                use_geolocation=False,
            )

        def track_spatial_structure(element, new_element):
            """Track spatial containment relationships."""
            for rel in getattr(element, "ContainedInStructure", []):
                container = rel.RelatingStructure
                new_container = append_asset(container)
                contained_ins.setdefault(container.GlobalId, set()).add(new_element)
                track_decomposition(container, new_container)

        def track_decomposition(element, new_element):
            """Track decomposition relationships."""
            for rel in element.Decomposes:
                parent = rel.RelatingObject
                new_parent = append_asset(parent)
                aggregates.setdefault(parent.GlobalId, set()).add(new_element)
                track_decomposition(parent, new_parent)
                track_spatial_structure(parent, new_parent)

        def copy_element(element):
            """Copy element with all relationships."""
            new_element = append_asset(element)
            if new_element:
                track_spatial_structure(element, new_element)
                track_decomposition(element, new_element)
            return new_element

        # Copy all selected elements
        # Progress: 5-90% for element copying (THIS IS THE SLOWEST PART - append_asset)
        for idx, element in enumerate(elements):
            if show_progress and idx % max(1, len(elements) // 80) == 0:
                progress = 5 + int(85 * idx / len(elements))
                bpy.context.window_manager.progress_update(progress)
            copy_element(element)
        
        # Progress: 90% after copying
        if show_progress:
            bpy.context.window_manager.progress_update(90)
        
        # Reconstruct spatial containment relationships
        for container_guid, related_elements in contained_ins.items():
            clipboard.createIfcRelContainedInSpatialStructure(
                ifcopenshell.guid.new(),
                owner_history,
                None,
                None,
                list(related_elements),
                clipboard.by_guid(container_guid),
            )

        # Reconstruct decomposition relationships
        if show_progress:
            bpy.context.window_manager.progress_update(91)
        
        for parent_guid, children in aggregates.items():
            clipboard.createIfcRelAggregates(
                ifcopenshell.guid.new(),
                owner_history,
                None,
                None,
                clipboard.by_guid(parent_guid),
                list(children),
            )

        # Progress: 92% before writing
        if show_progress:
            bpy.context.window_manager.progress_update(92)
        
        clipboard.write(output_path)
        
        # Progress: 95% after writing IFC file
        if show_progress:
            bpy.context.window_manager.progress_update(95)
        
        return clipboard


class CopyToClipboard(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_to_clipboard"
    bl_label = "Copy IFC Elements"
    bl_description = "Copy selected IFC elements to clipboard with all dependencies"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.selected_objects

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        elements_to_copy = []
        
        # Collect IFC elements from selected objects
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            
            # Handle grid axes - copy parent grid instead
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
            if not hasattr(element, "GlobalId") or not element.GlobalId:
                continue
            
            # Avoid duplicates
            if not any(e.id() == element.id() for obj, e in elements_to_copy):
                elements_to_copy.append((obj, element))
        
        if not elements_to_copy:
            self.report({"WARNING"}, "No IFC elements selected")
            return {"CANCELLED"}
        
        # Show progress for large operations
        total = len(elements_to_copy)
        show_progress = total > 20
        
        try:
            if show_progress:
                bpy.context.window_manager.progress_begin(0, 100)
                bpy.context.window_manager.progress_update(1)
            
            # Use clipboard engine for extraction
            engine = BonsaiGraphClipboardEngine(ifc_file)
            clipboard_ifc = get_clipboard_path("bonsai_clipboard.ifc")
            
            if show_progress:
                bpy.context.window_manager.progress_update(5)
            
            elements = [element for obj, element in elements_to_copy]
            engine.copy_to_file(ifc_file, elements, clipboard_ifc, show_progress)
            
            # Build metadata for clipboard
            # Progress: 95-97% for metadata building (fast)
            if show_progress:
                bpy.context.window_manager.progress_update(95)
            
            clipboard_data = {
                "version": 1,
                "schema": ifc_file.schema,
                "elements": []
            }
            
            for idx, (obj, element) in enumerate(elements_to_copy):
                matrix = obj.matrix_world.copy()
                container_element = ifcopenshell.util.element.get_container(element)
                
                clipboard_data["elements"].append({
                    "global_id": element.GlobalId,
                    "ifc_class": element.is_a(),
                    "name": element.Name or "",
                    "matrix": [float(v) for row in matrix for v in row],
                    "container_name": container_element.Name if container_element else None,
                    "container_class": container_element.is_a() if container_element else None,
                })
            
            # Progress: 97% complete metadata
            if show_progress:
                bpy.context.window_manager.progress_update(97)
            
            # Write metadata
            clipboard_json = get_clipboard_path("bonsai_clipboard.json")
            with open(clipboard_json, "w") as f:
                json.dump(clipboard_data, f, indent=2)
            
            # Progress: 98% after writing
            if show_progress:
                bpy.context.window_manager.progress_update(98)
            
            # Ensure clipboard UI sections are initialized
            try:
                if hasattr(context.scene, 'BIMClipboardProperties'):
                    context.scene.BIMClipboardProperties.ensure_sections()
            except Exception as e:
                # Non-critical - just log it
                import logging
                logging.getLogger("BIM").warning(f"Failed to initialize clipboard sections: {e}")
            
            # Progress: 100% complete
            if show_progress:
                bpy.context.window_manager.progress_update(100)
            
            self.report({"INFO"}, f"Copied {len(clipboard_data['elements'])} element(s)")
            return {"FINISHED"}
            
        except Exception as e:
            import logging
            logging.getLogger("BIM").exception("Error during copy operation")
            self.report({"ERROR"}, f"Copy failed: {str(e)}")
            return {"CANCELLED"}
        finally:
            # Always clean up progress indicator
            if show_progress:
                try:
                    bpy.context.window_manager.progress_end()
                except:
                    pass


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
        
        if not os.path.exists(clipboard_ifc):
            self.report({"ERROR"}, "Clipboard IFC not found")
            return {"CANCELLED"}
        
        try:
            with open(clipboard_json, "r") as f:
                clipboard_data = json.load(f)
            
            target = tool.Ifc.get()
            
            # Get paste mode from properties
            paste_mode = "DUPLICATE"
            try:
                if hasattr(context.scene, 'BIMClipboardProperties'):
                    paste_mode = context.scene.BIMClipboardProperties.paste_mode
            except Exception as e:
                import logging
                logging.getLogger("BIM").warning(f"Failed to get paste mode, using DUPLICATE: {e}")
            
            engine = BonsaiGraphClipboardEngine(target)
            
            new_elements = engine.paste_from_file(
                clipboard_ifc,
                clipboard_data,
                context,
                paste_mode
            )
            
            # Ensure all Blender data is properly updated before returning
            bpy.context.view_layer.update()
            
            if new_elements:
                self.report({"INFO"}, f"Pasted {len(new_elements)} element(s)")
            else:
                self.report({"WARNING"}, "Nothing pasted")
            
            return {"FINISHED"}
            
        except Exception as e:
            import logging
            logging.getLogger("BIM").exception("Error during paste operation")
            self.report({"ERROR"}, f"Paste failed: {str(e)}")
            return {"CANCELLED"}





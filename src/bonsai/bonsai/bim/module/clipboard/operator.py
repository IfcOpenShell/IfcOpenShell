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

    def paste_from_file(self, clipboard_ifc_path, clipboard_data, context):
        source = ifcopenshell.open(clipboard_ifc_path)
        roots = self._collect_safe_roots(source, clipboard_data)
        if not roots:
            return []
        total = len(roots)
        show_progress = total > 20
        if show_progress:
            bpy.context.window_manager.progress_begin(0, 100)
            bpy.context.window_manager.progress_update(1)
        new_elements = self._clone_graph(source, roots, show_progress)
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

    def _build_context_map(self, source, copied_entities, original_context_ids):
        context_map = {}
        original_contexts = [ctx for ctx in self.target.by_type("IfcGeometricRepresentationContext") 
                            if ctx.id() in original_context_ids]
        original_context_lookup = {}
        for context in original_contexts:
            if context.is_a("IfcGeometricRepresentationSubcontext"):
                parent = context.ParentContext
                key = (context.ContextType, context.ContextIdentifier, context.TargetView, 
                       parent.ContextType if parent else None)
            else:
                key = (context.ContextType, None, None, None)
            original_context_lookup[key] = context
        for entity in self.target.by_type("IfcGeometricRepresentationContext"):
            if entity.id() in original_context_ids:
                continue
            if entity.is_a("IfcGeometricRepresentationSubcontext"):
                parent = entity.ParentContext
                key = (entity.ContextType, entity.ContextIdentifier, entity.TargetView,
                       parent.ContextType if parent else None)
            else:
                key = (entity.ContextType, None, None, None)
            if key in original_context_lookup:
                context_map[entity.id()] = original_context_lookup[key]
        return context_map
    
    def _remap_representation_contexts(self, element, context_map):
        try:
            if element.Representation:
                for rep in element.Representation.Representations:
                    self._remap_single_representation(rep, context_map)
        except AttributeError:
            pass
        try:
            if element.RepresentationMaps:
                for rep_map in element.RepresentationMaps:
                    if rep_map.MappedRepresentation:
                        self._remap_single_representation(rep_map.MappedRepresentation, context_map)
        except AttributeError:
            pass
    
    def _remap_single_representation(self, rep, context_map):
        if not rep.ContextOfItems:
            return
        current_context = rep.ContextOfItems
        if current_context.id() in context_map:
            rep.ContextOfItems = context_map[current_context.id()]
            return
        if current_context.is_a("IfcGeometricRepresentationSubcontext"):
            parent = current_context.ParentContext
            for target_ctx in self.target.by_type("IfcGeometricRepresentationSubcontext"):
                if (target_ctx.ContextType == current_context.ContextType and
                    target_ctx.ContextIdentifier == current_context.ContextIdentifier and
                    target_ctx.TargetView == current_context.TargetView and
                    target_ctx.ParentContext.ContextType == (parent.ContextType if parent else None)):
                    rep.ContextOfItems = target_ctx
                    return
        else:
            for target_ctx in self.target.by_type("IfcGeometricRepresentationContext"):
                if (not target_ctx.is_a("IfcGeometricRepresentationSubcontext") and
                    target_ctx.ContextType == current_context.ContextType):
                    rep.ContextOfItems = target_ctx
                    return

    def _clone_graph(self, source, root_elements, show_progress=False):
        original_context_ids = {ctx.id() for ctx in self.target.by_type("IfcGeometricRepresentationContext")}
        copied_entities = {}
        guid_map = {}
        for root in root_elements:
            for element in source.traverse(root):
                if element.is_a("IfcRoot"):
                    if element.GlobalId not in guid_map:
                        guid_map[element.GlobalId] = ifcopenshell.guid.new()
        element_types = {}
        type_materials = {}
        element_psets = {}
        type_psets = {}
        for idx, root in enumerate(root_elements):
            if show_progress and idx % max(1, len(root_elements) // 20) == 0:
                progress = 1 + int(9 * idx / len(root_elements))
                bpy.context.window_manager.progress_update(progress)
            element_type = ifcopenshell.util.element.get_type(root)
            if element_type:
                if element_type.id() not in copied_entities:
                    copied_type = copy_deep(
                        self.target, 
                        element_type, 
                        copied_entities=copied_entities,
                    )
                    element_types[root.id()] = copied_type
                    type_material = ifcopenshell.util.element.get_material(element_type)
                    if type_material and type_material.id() not in copied_entities:
                        copy_deep(self.target, type_material, copied_entities=copied_entities)
                    type_materials_list = ifcopenshell.util.element.get_materials(element_type)
                    for mat in type_materials_list:
                        for material_rep in getattr(mat, 'HasRepresentation', []):
                            if material_rep.id() not in copied_entities:
                                copy_deep(self.target, material_rep, copied_entities=copied_entities)
                    for association in getattr(element_type, 'HasAssociations', []):
                        if association.is_a('IfcRelAssociatesMaterial'):
                            type_materials[element_type.id()] = association.RelatingMaterial
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
                else:
                    element_types[root.id()] = copied_entities[element_type.id()]
            material = ifcopenshell.util.element.get_material(root)
            if material:
                if material.id() not in copied_entities:
                    copy_deep(self.target, material, copied_entities=copied_entities)
            materials = ifcopenshell.util.element.get_materials(root)
            for mat in materials:
                for material_rep in getattr(mat, 'HasRepresentation', []):
                    if material_rep.id() not in copied_entities:
                        copy_deep(self.target, material_rep, copied_entities=copied_entities)
            try:
                if root.Representation:
                    for rep in root.Representation.Representations:
                        for item in rep.Items:
                            for styled_item in getattr(item, 'StyledByItem', []):
                                if styled_item.id() not in copied_entities:
                                    copy_deep(self.target, styled_item, copied_entities=copied_entities)
            except AttributeError:
                pass
            psets_for_element = []
            for rel in getattr(root, 'IsDefinedBy', []):
                if rel.is_a('IfcRelDefinesByProperties'):
                    pset = rel.RelatingPropertyDefinition
                    if pset.id() not in copied_entities:
                        copied_pset = copy_deep(self.target, pset, copied_entities=copied_entities)
                        psets_for_element.append(copied_pset)
                    else:
                        psets_for_element.append(copied_entities[pset.id()])
            if psets_for_element:
                element_psets[root.id()] = psets_for_element
        new_roots = []
        type_reconnections = []
        type_material_reconnections = []
        type_pset_reconnections = []
        material_reconnections = []
        pset_reconnections = []
        for idx, root in enumerate(root_elements):
            if show_progress and idx % max(1, len(root_elements) // 40) == 0:
                progress = 10 + int(60 * idx / len(root_elements))
                bpy.context.window_manager.progress_update(progress)
            new_root = copy_deep(
                self.target,
                root,
                copied_entities=copied_entities,
            )
            if root.id() in element_types:
                copied_type = element_types[root.id()]
                type_reconnections.append((new_root, copied_type))
                original_type = ifcopenshell.util.element.get_type(root)
                if original_type and original_type.id() in type_materials:
                    type_material = type_materials[original_type.id()]
                    if type_material.id() in copied_entities:
                        copied_type_material = copied_entities[type_material.id()]
                        type_material_reconnections.append((copied_type, copied_type_material))
                if original_type and original_type.id() in type_psets:
                    for pset in type_psets[original_type.id()]:
                        type_pset_reconnections.append((copied_type, pset))
            for association in getattr(root, 'HasAssociations', []):
                if association.is_a('IfcRelAssociatesMaterial'):
                    material = association.RelatingMaterial
                    if material.id() in copied_entities:
                        copied_material = copied_entities[material.id()]
                        material_reconnections.append((new_root, copied_material))
            if root.id() in element_psets:
                for pset in element_psets[root.id()]:
                    pset_reconnections.append((new_root, pset))
            for element in self.target.traverse(new_root):
                if element.is_a("IfcRoot"):
                    old_guid = element.GlobalId
                    if old_guid in guid_map:
                        element.GlobalId = guid_map[old_guid]
            new_roots.append(new_root)
        if show_progress:
            bpy.context.window_manager.progress_update(70)
        if type_reconnections:
            for new_root, copied_type in type_reconnections:
                ifcopenshell.api.run(
                    "type.assign_type",
                    self.target,
                    should_run_listeners=False,
                    related_objects=[new_root],
                    relating_type=copied_type,
                )
        if show_progress:
            bpy.context.window_manager.progress_update(72)
        if type_material_reconnections:
            type_material_groups = {}
            for copied_type, copied_material in type_material_reconnections:
                if copied_material.id() not in type_material_groups:
                    type_material_groups[copied_material.id()] = []
                type_material_groups[copied_material.id()].append(copied_type)
            for material_id, products in type_material_groups.items():
                copied_material = self.target.by_id(material_id)
                ifcopenshell.api.run(
                    "material.assign_material",
                    self.target,
                    should_run_listeners=False,
                    products=products,
                    material=copied_material,
                )
        if show_progress:
            bpy.context.window_manager.progress_update(74)
        if type_pset_reconnections:
            type_pset_groups = {}
            for copied_type, pset in type_pset_reconnections:
                if pset.id() not in type_pset_groups:
                    type_pset_groups[pset.id()] = []
                type_pset_groups[pset.id()].append(copied_type)
            for pset_id, products in type_pset_groups.items():
                pset = self.target.by_id(pset_id)
                ifcopenshell.api.run(
                    "pset.assign_pset",
                    self.target,
                    should_run_listeners=False,
                    products=products,
                    pset=pset,
                )
        if show_progress:
            bpy.context.window_manager.progress_update(76)
        if material_reconnections:
            material_groups = {}
            for new_root, copied_material in material_reconnections:
                if copied_material.id() not in material_groups:
                    material_groups[copied_material.id()] = []
                material_groups[copied_material.id()].append(new_root)
            for material_id, products in material_groups.items():
                copied_material = self.target.by_id(material_id)
                ifcopenshell.api.run(
                    "material.assign_material",
                    self.target,
                    should_run_listeners=False,
                    products=products,
                    material=copied_material,
                )
        if show_progress:
            bpy.context.window_manager.progress_update(78)
        if pset_reconnections:
            pset_groups = {}
            for new_root, pset in pset_reconnections:
                if pset.id() not in pset_groups:
                    pset_groups[pset.id()] = []
                pset_groups[pset.id()].append(new_root)
            for pset_id, products in pset_groups.items():
                pset = self.target.by_id(pset_id)
                ifcopenshell.api.run(
                    "pset.assign_pset",
                    self.target,
                    should_run_listeners=False,
                    products=products,
                    pset=pset,
                )
        if show_progress:
            bpy.context.window_manager.progress_update(80)
        old_guid_to_new_guid = {}
        for old_entity_id, new_entity in copied_entities.items():
            try:
                old_entity = source.by_id(old_entity_id)
                if old_entity.is_a("IfcRoot"):
                    old_guid_to_new_guid[old_entity.GlobalId] = new_entity.GlobalId
            except:
                pass
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
        if show_progress:
            bpy.context.window_manager.progress_update(81)
        context_map = self._build_context_map(source, copied_entities, original_context_ids)
        for copied_type in element_types.values():
            self._remap_representation_contexts(copied_type, context_map)
        for new_root in new_roots:
            self._remap_representation_contexts(new_root, context_map)
        for mat_def_rep in self.target.by_type("IfcMaterialDefinitionRepresentation"):
            if mat_def_rep.Representations:
                for rep in mat_def_rep.Representations:
                    if rep.ContextOfItems and rep.ContextOfItems.id() in context_map:
                        self._remap_single_representation(rep, context_map)
        if show_progress:
            bpy.context.window_manager.progress_update(83)
        duplicate_context_ids = set(context_map.keys())
        contexts_in_use = set()
        for rep in self.target.by_type("IfcRepresentation"):
            if rep.ContextOfItems:
                contexts_in_use.add(rep.ContextOfItems.id())
        removed_count = 0
        for ctx_id in duplicate_context_ids:
            if ctx_id not in contexts_in_use:
                ctx = self.target.by_id(ctx_id)
                if ctx:
                    if ctx.is_a("IfcGeometricRepresentationSubcontext"):
                        try:
                            self.target.remove(ctx)
                            removed_count += 1
                        except:
                            pass
                    else:
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
        return new_roots

    def _reattach_to_active_container(self, new_elements, context):
        active_container = tool.Spatial.get_active_container()
        if active_container and not active_container.is_a("IfcSpatialStructureElement"):
            active_container = None
        if not active_container:
            storeys = self.target.by_type("IfcBuildingStorey")
            if storeys:
                active_container = storeys[0]
            else:
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

    def _import_into_blender(self, new_elements):
        if not new_elements:
            return
        ifc_import_settings = import_ifc.IfcImportSettings.factory()
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.target
        ifc_importer.calculate_unit_scale()
        ifc_importer.process_context_filter()
        ifc_importer.material_creator.load_existing_materials()
        ifc_importer.create_styles()
        element_types = set()
        for element in new_elements:
            if element.is_a("IfcProduct"):
                element_type = ifcopenshell.util.element.get_type(element)
                if element_type:
                    element_types.add(element_type)
        if element_types:
            ifc_importer.element_types = element_types
            ifc_importer.create_element_types()
        products = set(e for e in new_elements if e.is_a("IfcProduct"))
        if products:
            ifc_importer.create_generic_elements(products)
            ifc_importer.setup_arrays()
            for obj in ifc_importer.added_data.values():
                if isinstance(obj, bpy.types.Object):
                    tool.Collector.assign(obj, should_clean_users_collection=False)

    def copy_to_file(self, source_file, elements, output_path, show_progress=False):
        clipboard = ifcopenshell.file(schema_version=source_file.schema_version)
        reuse_map = {}
        owner_history = None
        for oh in source_file.by_type("IfcOwnerHistory"):
            owner_history = clipboard.add(oh)
            break
        project = source_file.by_type("IfcProject")[0]
        clipboard.add(project)
        contained_ins = {}
        aggregates = {}

        def append_asset(element):
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
            for rel in getattr(element, "ContainedInStructure", []):
                container = rel.RelatingStructure
                new_container = append_asset(container)
                contained_ins.setdefault(container.GlobalId, set()).add(new_element)
                track_decomposition(container, new_container)

        def track_decomposition(element, new_element):
            for rel in element.Decomposes:
                parent = rel.RelatingObject
                new_parent = append_asset(parent)
                aggregates.setdefault(parent.GlobalId, set()).add(new_element)
                track_decomposition(parent, new_parent)
                track_spatial_structure(parent, new_parent)

        def copy_element(element):
            new_element = append_asset(element)
            if new_element:
                track_spatial_structure(element, new_element)
                track_decomposition(element, new_element)
            return new_element

        for idx, element in enumerate(elements):
            if show_progress and idx % max(1, len(elements) // 80) == 0:
                progress = 5 + int(85 * idx / len(elements))
                bpy.context.window_manager.progress_update(progress)
            copy_element(element)
        if show_progress:
            bpy.context.window_manager.progress_update(90)
        for container_guid, related_elements in contained_ins.items():
            clipboard.createIfcRelContainedInSpatialStructure(
                ifcopenshell.guid.new(),
                owner_history,
                None,
                None,
                list(related_elements),
                clipboard.by_guid(container_guid),
            )
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
        if show_progress:
            bpy.context.window_manager.progress_update(92)
        clipboard.write(output_path)
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
            if not hasattr(element, "GlobalId") or not element.GlobalId:
                continue
            if not any(e.id() == element.id() for obj, e in elements_to_copy):
                elements_to_copy.append((obj, element))
        if not elements_to_copy:
            self.report({"WARNING"}, "No IFC elements selected")
            return {"CANCELLED"}
        total = len(elements_to_copy)
        show_progress = total > 20
        if show_progress:
            bpy.context.window_manager.progress_begin(0, 100)
            bpy.context.window_manager.progress_update(1)
        engine = BonsaiGraphClipboardEngine(ifc_file)
        clipboard_ifc = get_clipboard_path("bonsai_clipboard.ifc")
        if show_progress:
            bpy.context.window_manager.progress_update(5)
        elements = [element for obj, element in elements_to_copy]
        engine.copy_to_file(ifc_file, elements, clipboard_ifc, show_progress)
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
        if show_progress:
            bpy.context.window_manager.progress_update(97)
        clipboard_json = get_clipboard_path("bonsai_clipboard.json")
        with open(clipboard_json, "w") as f:
            json.dump(clipboard_data, f, indent=2)
        if show_progress:
            bpy.context.window_manager.progress_update(98)
        context.scene.BIMClipboardProperties.ensure_sections()
        if show_progress:
            bpy.context.window_manager.progress_update(100)
            bpy.context.window_manager.progress_end()
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
        if not os.path.exists(clipboard_ifc):
            self.report({"ERROR"}, "Clipboard IFC not found")
            return {"CANCELLED"}
        with open(clipboard_json, "r") as f:
            clipboard_data = json.load(f)
        target = tool.Ifc.get()
        engine = BonsaiGraphClipboardEngine(target)
        new_elements = engine.paste_from_file(
            clipboard_ifc,
            clipboard_data,
            context
        )
        if new_elements:
            self.report({"INFO"}, f"Pasted {len(new_elements)} element(s)")
        else:
            self.report({"WARNING"}, "Nothing pasted")
        return {"FINISHED"}

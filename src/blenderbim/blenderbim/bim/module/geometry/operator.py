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

import bpy
import bmesh
import logging
import numpy as np
import json
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.api
import blenderbim.core.geometry as core
import blenderbim.core.aggregate
import blenderbim.core.style
import blenderbim.core.root
import blenderbim.core.drawing
import blenderbim.tool as tool
import blenderbim.bim.handler
from mathutils import Vector, Matrix
from time import time
from blenderbim.bim import import_ifc
from blenderbim.bim.ifc import IfcStore


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class EditObjectPlacement(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_object_placement"
    bl_label = "Edit Object Placement"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objs:
            core.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)


class OverrideMeshSeparate(bpy.types.Operator, Operator):
    bl_idname = "bim.override_mesh_separate"
    bl_label = "IFC Mesh Separate"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    type: bpy.props.StringProperty()

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        if not element:
            return

        # You cannot separate meshes if the representation is mapped.
        relating_type = tool.Root.get_element_type(element)
        if relating_type and tool.Root.does_type_have_representations(relating_type):
            # We toggle edit mode to ensure that once representations are
            # unmapped, our Blender mesh only has a single user.
            tool.Blender.toggle_edit_mode(context)
            bpy.ops.bim.unassign_type(related_object=obj.name)
            tool.Blender.toggle_edit_mode(context)

        selected_objects = context.selected_objects
        bpy.ops.mesh.separate(type=self.type)
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        new_objs = [obj]
        for new_obj in context.selected_objects:
            if new_obj == obj:
                continue
            # This is not very efficient, it needlessly copies the representations first.
            blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new_obj)
            new_objs.append(new_obj)
        for new_obj in new_objs:
            bpy.ops.bim.update_representation(obj=new_obj.name)


class OverrideOriginSet(bpy.types.Operator, Operator):
    bl_idname = "bim.override_origin_set"
    bl_label = "IFC Origin Set"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    origin_type: bpy.props.StringProperty()

    def _execute(self, context):
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if tool.Ifc.is_moved(obj):
                core.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
            representation = tool.Geometry.get_active_representation(obj)
            if not representation:
                continue
            representation = ifcopenshell.util.representation.resolve_representation(representation)
            if not tool.Geometry.is_meshlike(representation):
                continue
            bpy.ops.object.origin_set(type=self.origin_type)
            bpy.ops.bim.update_representation(obj=obj.name)


class AddRepresentation(bpy.types.Operator, Operator):
    bl_idname = "bim.add_representation"
    bl_label = "Add Representation"
    bl_options = {"REGISTER", "UNDO"}
    representation_conversion_method: bpy.props.EnumProperty(
        items=[
            ("OUTLINE", "Trace Outline", "Traces outline by local XY axes, for Profile - by local XZ axes."),
            (
                "BOX",
                "Bounding Box",
                "Creates a bounding box representation.\n"
                "For Plan context - 2D bounding box by local XY axes,\n"
                "for Profile - 2D bounding box by local XZ axes.\n"
                "For other contexts - bounding box is 3d.",
            ),
            ("PROJECT", "Full Representation", ""),
        ],
        name="Representation Conversion Method",
    )

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMGeometryProperties
        ifc_context = int(props.contexts or "0") or None
        if not ifc_context:
            return
        ifc_context = tool.Ifc.get().by_id(ifc_context)

        if self.representation_conversion_method == "OUTLINE":
            if ifc_context.ContextType == "Plan":
                data = tool.Geometry.generate_outline_mesh(obj, axis="+Z")
            elif ifc_context.ContextIdentifier == "Profile":
                data = tool.Geometry.generate_outline_mesh(obj, axis="-Y")
            else:
                data = tool.Geometry.generate_outline_mesh(obj, axis="+Z")
            tool.Geometry.change_object_data(obj, data, is_global=True)
        elif self.representation_conversion_method == "BOX":
            if ifc_context.ContextType == "Plan":
                data = tool.Geometry.generate_2d_box_mesh(obj, axis="Z")
            elif ifc_context.ContextIdentifier == "Profile":
                data = tool.Geometry.generate_2d_box_mesh(obj, axis="Y")
            else:
                data = tool.Geometry.generate_3d_box_mesh(obj)
            tool.Geometry.change_object_data(obj, data, is_global=True)

        core.add_representation(
            tool.Ifc,
            tool.Geometry,
            tool.Style,
            tool.Surveyor,
            obj=obj,
            context=ifc_context,
            ifc_representation_class=None,
            profile_set_usage=None,
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "representation_conversion_method", text="")


class SelectConnection(bpy.types.Operator, Operator):
    bl_idname = "bim.select_connection"
    bl_label = "Select Connection"
    bl_options = {"REGISTER", "UNDO"}
    connection: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_connection(tool.Geometry, connection=tool.Ifc.get().by_id(self.connection))


class RemoveConnection(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_connection"
    bl_label = "Remove Connection"
    bl_options = {"REGISTER", "UNDO"}
    connection: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_connection(tool.Geometry, connection=tool.Ifc.get().by_id(self.connection))


class SwitchRepresentation(bpy.types.Operator, Operator):
    bl_idname = "bim.switch_representation"
    bl_label = "Switch Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    ifc_definition_id: bpy.props.IntProperty()
    should_reload: bpy.props.BoolProperty()
    disable_opening_subtractions: bpy.props.BoolProperty()
    should_switch_all_meshes: bpy.props.BoolProperty()

    def _execute(self, context):
        target_representation = tool.Ifc.get().by_id(self.ifc_definition_id)
        target = target_representation.ContextOfItems
        is_subcontext = target.is_a("IfcGeometricRepresentationSubContext")
        for obj in set(context.selected_objects + [context.active_object]):
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if obj == context.active_object:
                representation = target_representation
            else:
                if is_subcontext:
                    representation = ifcopenshell.util.representation.get_representation(
                        element, target.ContextType, target.ContextIdentifier, target.TargetView
                    )
                else:
                    representation = ifcopenshell.util.representation.get_representation(element, target.ContextType)
            if not representation:
                continue
            core.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=self.should_reload,
                is_global=self.should_switch_all_meshes,
                should_sync_changes_first=True,
            )


class RemoveRepresentation(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_representation"
    bl_label = "Remove Representation"
    bl_options = {"REGISTER", "UNDO"}
    representation_id: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_representation(
            tool.Ifc,
            tool.Geometry,
            obj=context.active_object,
            representation=tool.Ifc.get().by_id(self.representation_id),
        )


class PurgeUnusedRepresentations(bpy.types.Operator, Operator):
    bl_idname = "bim.purge_unused_representations"
    bl_label = "Purge Unused Representations"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        purged_representations = core.purge_unused_representations(tool.Ifc, tool.Geometry)
        self.report({"INFO"}, f"{purged_representations} representations were purged.")


class UpdateRepresentation(bpy.types.Operator, Operator):
    bl_idname = "bim.update_representation"
    bl_label = "Update Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    ifc_representation_class: bpy.props.StringProperty()

    def _execute(self, context):
        if context.active_object and context.active_object.mode != "OBJECT":
            # Ensure mode is object to prevent invalid mesh data causing CTD
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        self.file = IfcStore.get_file()

        for obj in objs:
            # TODO: write unit tests to see how this bulk operation handles
            # contradictory ifc_representation_class values and when
            # ifc_representation_class is IfcTextLiteral
            if not obj.data:
                continue
            self.update_obj_mesh_representation(context, obj)
            IfcStore.edited_objs.discard(obj)
        return {"FINISHED"}

    def update_obj_mesh_representation(self, context, obj):
        product = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        material = ifcopenshell.util.element.get_material(product, should_skip_usage=True)

        if getattr(product, "HasOpenings", False) and obj.data.BIMMeshProperties.has_openings_applied:
            # Meshlike things with openings can only be updated without openings applied.
            return

        if not product.is_a("IfcGridAxis"):
            tool.Geometry.clear_cache(product)

        if product.is_a("IfcGridAxis"):
            # Grid geometry does not follow the "representation" paradigm and needs to be treated specially
            ifcopenshell.api.run("grid.create_axis_curve", self.file, **{"axis_curve": obj, "grid_axis": product})
            return
        elif product.is_a("IfcRelSpaceBoundary"):
            # TODO refactor
            settings = tool.Boundary.get_assign_connection_geometry_settings(obj)
            ifcopenshell.api.run("boundary.assign_connection_geometry", tool.Ifc.get(), **settings)
            return

        if tool.Ifc.is_moved(obj):
            core.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

        if material and material.is_a() in ["IfcMaterialProfileSet", "IfcMaterialLayerSet"]:
            if self.ifc_representation_class == "IfcTessellatedFaceSet":
                # We are explicitly casting to a tessellation, so remove all parametric materials.
                element_type = ifcopenshell.util.element.get_type(product)
                if element_type:  # Some invalid IFCs use material sets without a type.
                    ifcopenshell.api.run("material.unassign_material", tool.Ifc.get(), product=element_type)
                ifcopenshell.api.run("material.unassign_material", tool.Ifc.get(), product=product)
            else:
                # These objects are parametrically based on an axis and should not be modified as a mesh
                return

        old_representation = self.file.by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        context_of_items = old_representation.ContextOfItems

        # TODO: remove this code a bit later
        # added this as a fallback for easier transition some annotation types to 3d
        # if they were create before as 2d
        element = tool.Ifc.get_entity(obj)
        if tool.Drawing.is_annotation_object_type(element, ("FALL", "SECTION_LEVEL", "PLAN_LEVEL")):
            context_of_items = tool.Drawing.get_annotation_context("MODEL_VIEW")

        gprop = context.scene.BIMGeoreferenceProperties
        coordinate_offset = None
        if gprop.has_blender_offset and obj.BIMObjectProperties.blender_offset_type == "CARTESIAN_POINT":
            coordinate_offset = Vector(
                (
                    float(gprop.blender_eastings),
                    float(gprop.blender_northings),
                    float(gprop.blender_orthogonal_height),
                )
            )

        representation_data = {
            "context": context_of_items,
            "blender_object": obj,
            "geometry": obj.data,
            "coordinate_offset": coordinate_offset,
            "total_items": max(1, len(obj.material_slots)),
            "should_force_faceted_brep": tool.Geometry.should_force_faceted_brep(),
            "should_force_triangulation": tool.Geometry.should_force_triangulation(),
            "should_generate_uvs": tool.Geometry.should_generate_uvs(obj),
            "ifc_representation_class": self.ifc_representation_class,
        }

        if not self.ifc_representation_class:
            representation_data["ifc_representation_class"] = tool.Geometry.get_ifc_representation_class(
                product, old_representation
            )
            representation_data["profile_set_usage"] = tool.Geometry.get_profile_set_usage(product)
            representation_data["text_literal"] = tool.Geometry.get_text_literal(old_representation)

        new_representation = ifcopenshell.api.run("geometry.add_representation", self.file, **representation_data)

        if tool.Geometry.is_body_representation(new_representation):
            [
                tool.Geometry.run_style_add_style(obj=mat)
                for mat in tool.Geometry.get_object_materials_without_styles(obj)
            ]
            ifcopenshell.api.run(
                "style.assign_representation_styles",
                self.file,
                shape_representation=new_representation,
                styles=tool.Geometry.get_styles(obj, only_assigned_to_faces=True),
                should_use_presentation_style_assignment=context.scene.BIMGeometryProperties.should_use_presentation_style_assignment,
            )
            tool.Geometry.record_object_materials(obj)

        # TODO: move this into a replace_representation usecase or something
        for inverse in self.file.get_inverse(old_representation):
            ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)

        obj.data.BIMMeshProperties.ifc_definition_id = int(new_representation.id())
        obj.data.name = f"{old_representation.ContextOfItems.id()}/{new_representation.id()}"

        # TODO: In simple scenarios, a type has a ShapeRepresentation of ID
        # 123. This is then mapped through mapped representations by
        # occurrences, with no cartesian transformation. In this case, the mesh
        # data is 100% shared and therefore all have the same mesh name
        # referencing ID 123. (i.e. the local origins are shared). However, in
        # complex scenarios, occurrences may have their own cartesian
        # transformation (via MappingTarget). This will mean that occurrences
        # will not share the same mesh data and will instead reference a
        # different ShapeRepresentation ID. In this scenario, we have to
        # propagate the obj.data back to the type itself and all sibling
        # occurrences and accommodate their individual cartesian
        # transformations.

        core.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_representation)
        if obj.data.BIMMeshProperties.ifc_parameters:
            core.get_representation_ifc_parameters(tool.Geometry, obj=obj)


class UpdateParametricRepresentation(bpy.types.Operator):
    bl_idname = "bim.update_parametric_representation"
    bl_label = "Update Parametric Representation"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.mode == "OBJECT"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = context.active_object
        props = obj.data.BIMMeshProperties
        parameter = props.ifc_parameters[self.index]
        self.file.by_id(parameter.step_id)[parameter.index] = parameter.value
        show_representation_parameters = bool(props.ifc_parameters)
        core.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=tool.Ifc.get().by_id(props.ifc_definition_id),
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        if show_representation_parameters:
            core.get_representation_ifc_parameters(tool.Geometry, obj=obj)
        return {"FINISHED"}


class GetRepresentationIfcParameters(bpy.types.Operator, Operator):
    bl_idname = "bim.get_representation_ifc_parameters"
    bl_label = "Get Representation IFC Parameters"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.get_representation_ifc_parameters(tool.Geometry, obj=context.active_object)
        parameters = context.active_object.data.BIMMeshProperties.ifc_parameters
        self.report({"INFO"}, f"{len(parameters)} parameters found.")


class CopyRepresentation(bpy.types.Operator, Operator):
    bl_idname = "bim.copy_representation"
    bl_label = "Copy Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        if not context.active_object:
            return
        bm = bmesh.new()
        bm.from_mesh(context.active_object.data)
        geometric_context = tool.Root.get_representation_context(
            tool.Root.get_object_representation(context.active_object)
        )
        for obj in context.selected_objects:
            if obj == context.active_object:
                continue
            if obj.data:
                element = tool.Ifc.get_entity(obj)
                if not element:
                    continue
                bm.to_mesh(obj.data)
                old_rep = tool.Geometry.get_representation_by_context(element, geometric_context)
                if old_rep:
                    ifcopenshell.api.run(
                        "geometry.unassign_representation", tool.Ifc.get(), product=element, representation=old_rep
                    )
                    ifcopenshell.api.run("geometry.remove_representation", tool.Ifc.get(), representation=old_rep)
                core.add_representation(
                    tool.Ifc,
                    tool.Geometry,
                    tool.Style,
                    tool.Surveyor,
                    obj=obj,
                    context=geometric_context,
                    ifc_representation_class=None,
                    profile_set_usage=None,
                )


class OverrideDelete(bpy.types.Operator):
    bl_idname = "bim.override_object_delete"
    bl_label = "IFC Delete"
    bl_options = {"REGISTER", "UNDO"}
    use_global: bpy.props.BoolProperty(default=False)
    confirm: bpy.props.BoolProperty(default=True)
    is_batch: bpy.props.BoolProperty(name="Is Batch", default=False)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        # Deep magick from the dawn of time
        if tool.Ifc.get():
            return IfcStore.execute_ifc_operator(self, context)
        for obj in context.selected_objects:
            bpy.data.objects.remove(obj)
        # Required otherwise gizmos are still visible
        context.view_layer.objects.active = None
        return {"FINISHED"}

    def invoke(self, context, event):
        if tool.Ifc.get():
            total_elements = len(tool.Ifc.get().wrapped_data.entity_names())
            total_polygons = sum([len(o.data.polygons) for o in context.selected_objects if o.type == "MESH"])
            # These numbers are a bit arbitrary, but basically batching is only
            # really necessary on large models and large geometry removals.
            self.is_batch = total_elements > 500000 and total_polygons > 2000
            if self.is_batch:
                return context.window_manager.invoke_props_dialog(self)
            elif self.confirm:
                return context.window_manager.invoke_confirm(self, event)
        elif self.confirm:
            return context.window_manager.invoke_confirm(self, event)
        self.confirm = True
        return self.execute(context)

    def draw(self, context):
        row = self.layout.row()
        row.label(text="Warning: Faster deletion will use more memory.", icon="ERROR")
        row = self.layout.row()
        row.prop(self, "is_batch", text="Enable Faster Deletion")

    def _execute(self, context):
        if self.is_batch:
            ifcopenshell.util.element.batch_remove_deep2(tool.Ifc.get())

        self.process_arrays(context)
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                if ifcopenshell.util.element.get_pset(element, "BBIM_Array"):
                    self.report({"INFO"}, "Elements that are part of an array cannot be deleted.")
                    return {"FINISHED"}
                tool.Geometry.delete_ifc_object(obj)
            else:
                bpy.data.objects.remove(obj)

        if self.is_batch:
            old_file = tool.Ifc.get()
            old_file.end_transaction()
            new_file = ifcopenshell.util.element.unbatch_remove_deep2(tool.Ifc.get())
            new_file.begin_transaction()
            tool.Ifc.set(new_file)
            self.transaction_data = {"old_file": old_file, "new_file": new_file}
            IfcStore.add_transaction_operation(self)
        # Required otherwise gizmos are still visible
        context.view_layer.objects.active = None
        return {"FINISHED"}

    def rollback(self, data):
        tool.Ifc.set(data["old_file"])
        data["old_file"].undo()

    def commit(self, data):
        data["old_file"].redo()
        tool.Ifc.set(data["new_file"])

    def process_arrays(self, context):
        selected_objects = set(context.selected_objects)
        array_parents = set()
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            if not pset:
                continue
            array_parents.add(tool.Ifc.get().by_guid(pset["Parent"]))

        for array_parent in array_parents:
            array_parent_obj = tool.Ifc.get_object(array_parent)
            data = [(i, data) for i, data in enumerate(tool.Blender.Modifier.Array.get_modifiers_data(array_parent))]
            # NOTE: there is a way to remove arrays more precisely but it's more complex
            for i, modifier_data in reversed(data):
                children = set(tool.Blender.Modifier.Array.get_children_objects(modifier_data))
                if children.issubset(selected_objects):
                    with context.temp_override(active_object=array_parent_obj):
                        bpy.ops.bim.remove_array(item=i)
                else:
                    break  # allows to remove only n last layers of an array


class OverrideOutlinerDelete(bpy.types.Operator):
    bl_idname = "bim.override_outliner_delete"
    bl_label = "IFC Delete"
    bl_options = {"REGISTER", "UNDO"}
    hierarchy: bpy.props.BoolProperty(default=False)
    is_batch: bpy.props.BoolProperty(name="Is Batch", default=False)

    @classmethod
    def poll(cls, context):
        return len(getattr(context, "selected_ids", [])) > 0

    def execute(self, context):
        # In this override, we don't check self.hierarchy. This effectively
        # makes Delete and Delete Hierarchy identical. This is on purpose, since
        # non-hierarchical deletion may imply a whole bunch of potentially
        # unintended IFC spatial modifications. To make life less confusing for
        # the user, Delete means Delete. End of story.
        # Deep magick from the dawn of time
        if IfcStore.get_file():
            return IfcStore.execute_ifc_operator(self, context)
        # https://blender.stackexchange.com/questions/203729/python-get-selected-objects-in-outliner
        objects_to_delete = set()
        collections_to_delete = set()
        for item in context.selected_ids:
            if item.bl_rna.identifier == "Collection":
                collection = bpy.data.collections.get(item.name)
                collection_data = self.get_collection_objects_and_children(collection)
                objects_to_delete |= collection_data["objects"]
                collections_to_delete |= collection_data["children"]
                collections_to_delete.add(collection)
            elif item.bl_rna.identifier == "Object":
                objects_to_delete.add(bpy.data.objects.get(item.name))
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj)
        for collection in collections_to_delete:
            bpy.data.collections.remove(collection)
        return {"FINISHED"}

    def invoke(self, context, event):
        if tool.Ifc.get():
            total_elements = len(tool.Ifc.get().wrapped_data.entity_names())
            total_polygons = sum([len(o.data.polygons) for o in context.selected_objects if o.type == "MESH"])
            # These numbers are a bit arbitrary, but basically batching is only
            # really necessary on large models and large geometry removals.
            self.is_batch = total_elements > 500000 and total_polygons > 2000
            if self.is_batch:
                return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        row = self.layout.row()
        row.label(text="Warning: Faster deletion will use more memory.", icon="ERROR")
        row = self.layout.row()
        row.prop(self, "is_batch", text="Enable Faster Deletion")

    def _execute(self, context):
        if self.is_batch:
            ifcopenshell.util.element.batch_remove_deep2(tool.Ifc.get())
        objects_to_delete = set()
        collections_to_delete = set()
        for item in context.selected_ids:
            if item.bl_rna.identifier == "Collection":
                collection = bpy.data.collections.get(item.name)
                collection_data = self.get_collection_objects_and_children(collection)
                objects_to_delete |= collection_data["objects"]
                collections_to_delete |= collection_data["children"]
                collections_to_delete.add(collection)
            elif item.bl_rna.identifier == "Object":
                objects_to_delete.add(bpy.data.objects.get(item.name))
        for obj in objects_to_delete:
            if tool.Ifc.get_entity(obj):
                tool.Geometry.delete_ifc_object(obj)
            else:
                bpy.data.objects.remove(obj)
        for collection in collections_to_delete:
            bpy.data.collections.remove(collection)
        if self.is_batch:
            old_file = tool.Ifc.get()
            old_file.end_transaction()
            new_file = ifcopenshell.util.element.unbatch_remove_deep2(tool.Ifc.get())
            new_file.begin_transaction()
            tool.Ifc.set(new_file)
            self.transaction_data = {"old_file": old_file, "new_file": new_file}
            IfcStore.add_transaction_operation(self)
        return {"FINISHED"}

    def get_collection_objects_and_children(self, collection):
        objects = set()
        children = set()
        queue = [collection]
        while queue:
            collection = queue.pop()
            for obj in collection.objects:
                objects.add(obj)
            queue.extend(collection.children)
            children = children.union(collection.children)
        return {"objects": objects, "children": children}

    def rollback(self, data):
        tool.Ifc.set(data["old_file"])
        data["old_file"].undo()

    def commit(self, data):
        data["old_file"].redo()
        tool.Ifc.set(data["new_file"])


class OverrideDuplicateMoveMacro(bpy.types.Macro):
    bl_idname = "bim.override_object_duplicate_move_macro"
    bl_label = "IFC Duplicate Objects"
    bl_options = {"REGISTER", "UNDO"}


class OverrideDuplicateMove(bpy.types.Operator):
    bl_idname = "bim.override_object_duplicate_move"
    bl_label = "IFC Duplicate Objects"
    bl_options = {"REGISTER", "UNDO"}
    is_interactive: bpy.props.BoolProperty(name="Is Interactive", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        return OverrideDuplicateMove.execute_duplicate_operator(self, context, linked=False)

    def _execute(self, context):
        return OverrideDuplicateMove.execute_ifc_duplicate_operator(self, context)

    @staticmethod
    def execute_duplicate_operator(self, context, linked=False):
        # Deep magick from the dawn of time
        if IfcStore.get_file():
            IfcStore.execute_ifc_operator(self, context)
            if self.new_active_obj:
                context.view_layer.objects.active = self.new_active_obj
            return {"FINISHED"}

        new_active_obj = None
        for obj in context.selected_objects:
            new_obj = obj.copy()
            if obj.data and not linked:
                new_obj.data = obj.data.copy()
            if obj == context.active_object:
                new_active_obj = new_obj
            for collection in obj.users_collection:
                collection.objects.link(new_obj)
            obj.select_set(False)
            new_obj.select_set(True)
        if new_active_obj:
            context.view_layer.objects.active = new_active_obj
        return {"FINISHED"}

    @staticmethod
    def execute_ifc_duplicate_operator(self, context, linked=False):
        objects_to_duplicate = set(context.selected_objects)

        # handle arrays
        arrays_to_duplicate, array_children = OverrideDuplicateMove.process_arrays(self, context)
        objects_to_duplicate -= array_children
        for child in array_children:
            child.select_set(False)

        self.new_active_obj = None
        # Track decompositions so they can be recreated after the operation
        relationships = tool.Root.get_decomposition_relationships(objects_to_duplicate)
        old_to_new = {}

        for obj in objects_to_duplicate:
            element = tool.Ifc.get_entity(obj)
            if element and element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
                continue  # For now, don't copy drawings until we stabilise a bit more. It's tricky.

            linked_non_ifc_object = linked and not element

            # Prior to duplicating, sync the object placement to make decomposition recreation more stable.
            if tool.Ifc.is_moved(obj):
                blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

            new_obj = obj.copy()
            temp_data = None

            if obj.data and not linked_non_ifc_object:
                # assure root.copy_class won't replace the previous mesh globally
                temp_data = obj.data.copy()
                new_obj.data = temp_data

            if obj == context.active_object:
                self.new_active_obj = new_obj
            for collection in obj.users_collection:
                collection.objects.link(new_obj)
            obj.select_set(False)
            new_obj.select_set(True)

            if linked_non_ifc_object:
                continue

            # clear object's collection so it will be able to have it's own
            new_obj.BIMObjectProperties.collection = None
            # copy the actual class
            new = blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new_obj)

            # clean up the orphaned mesh with ifc id of the original object to avoid confusion
            # IfcGridAxis keeps the same mesh data (it's pointing to ifc id 0, so it's not a problem)
            if new and temp_data and not new.is_a("IfcGridAxis"):
                tool.Blender.remove_data_block(temp_data)

            if new:
                # TODO: handle array data for other cases of duplication
                array_data = arrays_to_duplicate.get(obj, None)
                tool.Model.handle_array_on_copied_element(new, array_data)
                if array_data:
                    for child in tool.Blender.Modifier.Array.get_all_children_objects(new):
                        child.select_set(True)

                # TODO: add new array children to recreate their decomposition too
                old_to_new[element] = [new]
                if new.is_a("IfcRelSpaceBoundary"):
                    tool.Boundary.decorate_boundary(new_obj)

        # Recreate decompositions
        tool.Root.recreate_decompositions(relationships, old_to_new)
        blenderbim.bim.handler.refresh_ui_data()

    @staticmethod
    def process_arrays(self, context):
        selected_objects = set(context.selected_objects)
        array_parents = set()
        arrays_to_create = dict()
        array_children = set()  # will be ignored during the duplication

        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            if not pset:
                continue
            array_parents.add(tool.Ifc.get().by_guid(pset["Parent"]))

        for array_parent in array_parents:
            array_parent_obj = tool.Ifc.get_object(array_parent)
            if array_parent_obj not in selected_objects:
                continue

            array_data = []
            for modifier_data in tool.Blender.Modifier.Array.get_modifiers_data(array_parent):
                children = set(tool.Blender.Modifier.Array.get_children_objects(modifier_data))
                if children.issubset(selected_objects):
                    modifier_data["children"] = []
                    array_data.append(modifier_data)
                    array_children.update(children)
                else:
                    break  # allows to duplicate only n first layers of an array

            if array_data:
                arrays_to_create[array_parent_obj] = array_data

        return arrays_to_create, array_children


class OverrideDuplicateMoveLinkedMacro(bpy.types.Macro):
    bl_idname = "bim.override_object_duplicate_move_linked_macro"
    bl_label = "IFC Duplicate Linked"
    bl_options = {"REGISTER", "UNDO"}


class OverrideDuplicateMoveLinked(bpy.types.Operator):
    bl_idname = "bim.override_object_duplicate_move_linked"
    bl_label = "IFC Duplicate Linked"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        return OverrideDuplicateMove.execute_duplicate_operator(self, context, linked=True)

    def _execute(self, context):
        return OverrideDuplicateMove.execute_ifc_duplicate_operator(self, context, linked=True)


class OverrideDuplicateMoveAggregateMacro(bpy.types.Macro):
    bl_idname = "bim.override_object_duplicate_move_aggregate_macro"
    bl_label = "IFC Duplicate Objects Aggregate"
    bl_options = {"REGISTER", "UNDO"}


class OverrideDuplicateMoveAggregate(bpy.types.Operator):
    bl_idname = "bim.override_object_duplicate_move_aggregate"
    bl_label = "IFC Duplicate Objects Aggregate"
    bl_options = {"REGISTER", "UNDO"}
    is_interactive: bpy.props.BoolProperty(name="Is Interactive", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        return OverrideDuplicateMove.execute_duplicate_operator(self, context, linked=False)

    def _execute(self, context):
        self.new_active_obj = None
        old_to_new = {}

        ### Adding the assembly data
        def add_assembly_data(element, parent, data_to_add):
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_Aggregate_Data")
            data = [data_to_add]

            if pset:
                if parent == None:
                    ifcopenshell.api.run(
                        "pset.edit_pset",
                        tool.Ifc.get(),
                        pset=tool.Ifc.get().by_id(pset["id"]),
                        properties={"Data": tool.Ifc.get().createIfcText(json.dumps(data))},
                    )
                else:
                    ifcopenshell.api.run(
                        "pset.edit_pset",
                        tool.Ifc.get(),
                        pset=tool.Ifc.get().by_id(pset["id"]),
                        properties={"Parent": parent.GlobalId, "Data": tool.Ifc.get().createIfcText(json.dumps(data))},
                    )

            else:
                pset = ifcopenshell.api.run(
                    "pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Aggregate_Data"
                )

                ifcopenshell.api.run(
                    "pset.edit_pset",
                    tool.Ifc.get(),
                    pset=pset,
                    properties={"Parent": parent.GlobalId, "Data": tool.Ifc.get().createIfcText(json.dumps(data))},
                )

        def add_child_to_assembly_data(new_entity):
            pset = ifcopenshell.util.element.get_pset(new_entity, "BBIM_Aggregate_Data")
            parent_element = tool.Ifc.get().by_guid(pset["Parent"])
            parent_pset = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Aggregate_Data")
            data = json.loads(parent_pset["Data"])
            data[0]["children"].append(new_entity.GlobalId)

            ifcopenshell.api.run(
                "pset.edit_pset",
                tool.Ifc.get(),
                pset=tool.Ifc.get().by_id(parent_pset["id"]),
                properties={"Data": tool.Ifc.get().createIfcText(json.dumps(data))},
            )

        def create_data_structure(entity, level=-1):
            level += 1

            data_children = {
                "children": [],
                "instance_of": [],
            }

            data_parent = {
                "children": [],
                "instance_of": [entity.GlobalId],
            }

            if not entity.is_a("IfcElementAssembly"):
                return
            else:
                if level == 0:
                    add_assembly_data(entity, entity, data_parent)
                else:
                    add_assembly_data(entity, None, data_parent)
                parts = ifcopenshell.util.element.get_parts(entity)
                for part in parts:
                    if part.is_a("IfcElementAssembly"):
                        add_assembly_data(part, entity, data_children)
                        add_child_to_assembly_data(part)
                        create_data_structure(part, level)
                        continue
                    add_assembly_data(part, entity, data_children)
                    add_child_to_assembly_data(part)

                return

        def recreate_data_structure(entity, level=-1):
            level += 1

            pset = ifcopenshell.util.element.get_pset(entity, "BBIM_Aggregate_Data")
            pset_data = json.loads(pset["Data"])[0]
            instance_of = pset_data["instance_of"]

            data_children = {
                "children": [],
                "instance_of": [],
            }

            # Keeps instance ID through all copies
            data_parent = {
                "children": [],
                "instance_of": instance_of,
            }

            if not entity.is_a("IfcElementAssembly"):
                return
            else:
                if level == 0:
                    add_assembly_data(entity, entity, data_parent)
                else:
                    add_assembly_data(entity, None, data_parent)
                parts = ifcopenshell.util.element.get_parts(entity)
                for part in parts:
                    if part.is_a("IfcElementAssembly"):
                        add_child_to_assembly_data(part)
                        recreate_data_structure(part, level)
                        continue
                    add_assembly_data(part, entity, data_children)
                    add_child_to_assembly_data(part)

                return

        def duplicate_all(obj, level=-1, new_parent=None, parents=[]):
            level += 1

            entity = tool.Ifc.get_entity(obj)

            if level == 0:
                new_parent = duplicate_objects(obj)
                parents.append(new_parent)
            else:
                pair = []
                pair.append(new_parent)
                new_parent = duplicate_objects(obj)
                pair.append(new_parent)
                parents.append(pair)

            if not entity.is_a("IfcElementAssembly"):
                return
            else:
                parts = ifcopenshell.util.element.get_parts(entity)

                # Ensures that we are duplication all the IfcElementAssembly
                # before duplicating the nested objects
                for part in parts:
                    if part.is_a("IfcElementAssembly"):
                        pass
                    else:
                        part_obj = tool.Ifc.get_object(part)
                        new_part = duplicate_objects(part_obj)
                        blenderbim.core.aggregate.assign_object(
                            tool.Ifc,
                            tool.Aggregate,
                            tool.Collector,
                            relating_obj=tool.Ifc.get_object(new_parent),
                            related_obj=tool.Ifc.get_object(new_part),
                        )

                for part in parts:
                    if part.is_a("IfcElementAssembly"):
                        part_obj = tool.Ifc.get_object(part)

                        # Recursion Call
                        duplicate_all(part_obj, level, new_parent, parents)

            if level == 0:
                for p in parents[1:]:
                    blenderbim.core.aggregate.assign_object(
                        tool.Ifc,
                        tool.Aggregate,
                        tool.Collector,
                        relating_obj=tool.Ifc.get_object(p[0]),
                        related_obj=tool.Ifc.get_object(p[1]),
                    )

                return new_parent
            return

        def duplicate_objects(obj, is_root=False):
            new_obj = obj.copy()
            if obj.data:
                new_obj.data = obj.data.copy()
            if obj == context.active_object:
                self.new_active_obj = new_obj
            for collection in obj.users_collection:
                collection.objects.link(new_obj)
            obj.select_set(False)
            new_obj.select_set(True)

            # This is needed to make sure the new object gets unlink from
            # the old object assembly collection
            new_obj.BIMObjectProperties.collection = None

            # Copy the actual class
            new_entity = blenderbim.core.root.copy_class(
                tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new_obj
            )

            if new_entity:
                tool.Model.handle_array_on_copied_element(new_entity)
                blenderbim.core.aggregate.unassign_object(
                    tool.Ifc,
                    tool.Aggregate,
                    tool.Collector,
                    relating_obj=tool.Ifc.get_object(selected_root_entity),
                    related_obj=tool.Ifc.get_object(new_entity),
                )

                old_to_new[tool.Ifc.get_entity(obj)] = [new_entity]

            return new_entity

        ### Check if only one element and it's assembly
        if len(context.selected_objects) != 1:
            return {"FINISHED"}

        selected_obj = context.selected_objects[0]
        selected_root_entity = tool.Ifc.get_entity(selected_obj)

        if not selected_root_entity.is_a("IfcElementAssembly"):
            return {"FINISHED"}

        pset = ifcopenshell.util.element.get_pset(selected_root_entity, "BBIM_Aggregate_Data")
        if not pset:
            create_data_structure(selected_root_entity)

        pset = ifcopenshell.util.element.get_pset(selected_root_entity, "BBIM_Aggregate_Data")

        selected_root_parent = selected_root_entity

        new_root_entity = duplicate_all(selected_obj)

        recreate_data_structure(new_root_entity)

        # Remove connections with old objects
        for new in old_to_new.values():
            for connection in new[0].ConnectedTo:
                entity = connection.RelatedElement
                if entity in old_to_new.keys():
                    core.remove_connection(tool.Geometry, connection=connection)
            for connection in new[0].ConnectedFrom:
                entity = connection.RelatingElement
                if entity in old_to_new.keys():
                    core.remove_connection(tool.Geometry, connection=connection)

        old_objs = []
        for old, new in old_to_new.items():
            old_objs.append(tool.Ifc.get_object(old))

        relationships = tool.Root.get_decomposition_relationships(old_objs)

        tool.Root.recreate_decompositions(relationships, old_to_new)

        blenderbim.bim.handler.refresh_ui_data()

        return {"FINISHED"}


class RefreshAggregate(bpy.types.Operator):
    bl_idname = "bim.refresh_aggregate"
    bl_label = "IFC Refresh Aggregate"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        # Deep magick from the dawn of time
        if IfcStore.get_file():
            IfcStore.execute_ifc_operator(self, context)
            return {"FINISHED"}

        return {"FINISHED"}

    def _execute(self, context):
        refresh_start_time = time()
        self.new_active_obj = None
        old_to_new = {}

        def remove_objects(entity, level=-1, parents=[]):
            level += 1
            if level == 0:
                parents = [entity]
            parts = ifcopenshell.util.element.get_parts(entity)
            for part in parts:
                if part.is_a("IfcElementAssembly"):
                    parents.append(part)
                    remove_objects(part, level, parents)
                    continue
                else:
                    part_obj = tool.Ifc.get_object(part)
                    if part_obj:
                        tool.Geometry.delete_ifc_object(part_obj)

            return parents

        def duplicate_children(entity):
            pset = ifcopenshell.util.element.get_pset(entity, "BBIM_Aggregate_Data")
            pset_data = json.loads(pset["Data"])[0]
            instance_of = pset_data["instance_of"][0]

            instance_entity = tool.Ifc.get().by_guid(instance_of)

            if not instance_entity.is_a("IfcElementAssembly"):
                return
            else:
                parts = ifcopenshell.util.element.get_parts(instance_entity)
                for part in parts:
                    pset = ifcopenshell.util.element.get_pset(part, "BBIM_Aggregate_Data")
                    if part.is_a("IfcElementAssembly"):
                        if not pset:
                            data_children = {
                                "children": [],
                                "instance_of": [part.GlobalId],
                            }
                            data = [data_children]

                            pset = ifcopenshell.api.run(
                                "pset.add_pset", tool.Ifc.get(), product=part, name="BBIM_Aggregate_Data"
                            )
                            ifcopenshell.api.run(
                                "pset.edit_pset",
                                tool.Ifc.get(),
                                pset=pset,
                                properties={
                                    "Parent": instance_entity.GlobalId,
                                    "Data": tool.Ifc.get().createIfcText(json.dumps(data)),
                                },
                            )

                            part_obj = tool.Ifc.get_object(part)
                            new_part = duplicate_objects(part_obj)

                            blenderbim.core.aggregate.assign_object(
                                tool.Ifc,
                                tool.Aggregate,
                                tool.Collector,
                                relating_obj=tool.Ifc.get_object(entity),
                                related_obj=tool.Ifc.get_object(new_part),
                            )
                            duplicate_children(new_part)

                for part in parts:
                    pset = ifcopenshell.util.element.get_pset(part, "BBIM_Aggregate_Data")
                    if part.is_a("IfcElementAssembly"):
                        pass

                    else:
                        if not pset:
                            pset = ifcopenshell.api.run(
                                "pset.add_pset", tool.Ifc.get(), product=part, name="BBIM_Aggregate_Data"
                            )
                        else:
                            pset = ifcopenshell.util.element.get_pset(part, "BBIM_Aggregate_Data")
                            pset = tool.Ifc.get().by_id(pset["id"])

                        data_children = {
                            "children": [],
                            "instance_of": [],
                        }
                        data = [data_children]

                        ifcopenshell.api.run(
                            "pset.edit_pset",
                            tool.Ifc.get(),
                            pset=pset,
                            properties={
                                "Parent": instance_entity.GlobalId,
                                "Data": tool.Ifc.get().createIfcText(json.dumps(data)),
                            },
                        )

                        part_obj = tool.Ifc.get_object(part)
                        new_part = duplicate_objects(part_obj)
                        blenderbim.core.aggregate.assign_object(
                            tool.Ifc,
                            tool.Aggregate,
                            tool.Collector,
                            relating_obj=tool.Ifc.get_object(entity),
                            related_obj=tool.Ifc.get_object(new_part),
                        )

        def duplicate_objects(obj, is_root=False):
            new_obj = obj.copy()
            if obj.data:
                new_obj.data = obj.data.copy()
            if obj == context.active_object:
                self.new_active_obj = new_obj
            for collection in obj.users_collection:
                collection.objects.link(new_obj)
            obj.select_set(False)
            new_obj.select_set(True)

            # This is needed to make sure the new object gets unlink from
            # the old object assembly collection
            new_obj.BIMObjectProperties.collection = None

            # Copy the actual class
            new_entity = blenderbim.core.root.copy_class(
                tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new_obj
            )

            if new_entity:
                tool.Model.handle_array_on_copied_element(new_entity)

                if not new_entity.is_a("IfcElementAssembly"):
                    blenderbim.core.aggregate.unassign_object(
                        tool.Ifc,
                        tool.Aggregate,
                        tool.Collector,
                        relating_obj=obj,
                        related_obj=tool.Ifc.get_object(new_entity),
                    )

                old_to_new[tool.Ifc.get_entity(obj)] = [new_entity]

            return new_entity

        if len(context.selected_objects) != 1:
            self.report({"INFO"}, "Only 1 object need to be selected.")
            return {"FINISHED"}

        selected_root_obj = context.selected_objects[0]
        selected_root_entity = tool.Ifc.get_entity(selected_root_obj)

        if selected_root_entity.is_a("IfcElementAssembly"):
            pass
        elif selected_root_entity.Decomposes:
            if selected_root_entity.Decomposes[0].RelatingObject.is_a("IfcElementAssembly"):
                selected_root_entity = selected_root_entity.Decomposes[0].RelatingObject
                selected_root_obj = tool.Ifc.get_object(selected_root_entity)
        else:
            self.report({"INFO"}, "Object is not part of a IfcElementAssembly.")
            return {"FINISHED"}

        pset = ifcopenshell.util.element.get_pset(selected_root_entity, "BBIM_Aggregate_Data")
        if not pset:
            self.report({"INFO"}, "Object is not part of an assembly aggregate.")
            return {"FINISHED"}

        pset_data = json.loads(pset["Data"])[0]
        instance_of = pset_data["instance_of"][0]
        original_root_entity = tool.Ifc.get().by_guid(instance_of)
        if original_root_entity == selected_root_entity:
            self.report({"INFO"}, "Cannot refresh original assembly. Select an assembly instance.")
            return {"FINISHED"}

        parents = remove_objects(selected_root_entity)

        original_root_object = tool.Ifc.get_object(original_root_entity)

        selected_matrix = selected_root_obj.matrix_world
        original_matrix = original_root_object.matrix_world

        for parent in parents:
            duplicate_children(parent)

        # Remove connections with old objects
        for new in old_to_new.values():
            for connection in new[0].ConnectedTo:
                entity = connection.RelatedElement
                if entity in old_to_new.keys():
                    core.remove_connection(tool.Geometry, connection=connection)
            for connection in new[0].ConnectedFrom:
                entity = connection.RelatingElement
                if entity in old_to_new.keys():
                    core.remove_connection(tool.Geometry, connection=connection)

        old_objs = []
        for old, new in old_to_new.items():
            old_objs.append(tool.Ifc.get_object(old))

            new_obj = tool.Ifc.get_object(new[0])

            matrix_diff = Matrix.inverted(original_matrix) @ new_obj.matrix_world
            new_matrix = selected_matrix @ matrix_diff

            new_obj.matrix_world = new_matrix

        relationships = tool.Root.get_decomposition_relationships(old_objs)

        tool.Root.recreate_decompositions(relationships, old_to_new)

        blenderbim.bim.handler.refresh_ui_data()

        operator_time = time() - refresh_start_time
        if operator_time > 10:
            self.report({"INFO"}, "Refresh Aggregate was finished in {:.2f} seconds".format(operator_time))
        return {"FINISHED"}


class OverrideJoin(bpy.types.Operator, Operator):
    bl_idname = "bim.override_object_join"
    bl_label = "IFC Join"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if not tool.Ifc.get():
            return bpy.ops.object.join()
        return self.execute(context)

    def _execute(self, context):
        if not tool.Ifc.get():
            return bpy.ops.object.join()

        if not context.active_object:
            return

        self.target = context.active_object
        self.target_element = tool.Ifc.get_entity(self.target)
        if self.target_element:
            return self.join_ifc_obj()
        return self.join_blender_obj()

    def join_ifc_obj(self):
        representation = tool.Ifc.get().by_id(self.target.data.BIMMeshProperties.ifc_definition_id)
        if representation.RepresentationType in ("Tessellation", "Brep"):
            for obj in bpy.context.selected_objects:
                if obj == self.target:
                    continue
                element = tool.Ifc.get_entity(obj)
                if element:
                    ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)
            bpy.ops.object.join()
            bpy.ops.bim.update_representation(obj=self.target.name, ifc_representation_class="")
        elif representation.RepresentationType == "SweptSolid":
            target_placement = np.array(self.target.matrix_world)
            items = list(representation.Items)
            for obj in bpy.context.selected_objects:
                if obj == self.target:
                    continue
                element = tool.Ifc.get_entity(obj)

                # Non IFC elements cannot be joined since we cannot guarantee SweptSolid compliance
                if not element:
                    obj.select_set(False)
                    continue

                # Only objects of the same representation type can be joined
                obj_rep = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
                if obj_rep.RepresentationType != "SweptSolid":
                    obj.select_set(False)
                    continue

                placement = np.array(obj.matrix_world)

                for item in obj_rep.Items:
                    copied_item = ifcopenshell.util.element.copy_deep(tool.Ifc.get(), item)
                    for style in item.StyledByItem:
                        copied_style = ifcopenshell.util.element.copy(tool.Ifc.get(), style)
                        copied_style.Item = copied_item
                    if copied_item.Position:
                        position = ifcopenshell.util.placement.get_axis2placement(copied_item.Position)
                    else:
                        position = np.eye(4)
                    position = placement @ position
                    position = np.linalg.inv(target_placement) @ position
                    copied_item.Position = tool.Ifc.get().createIfcAxis2Placement3D(
                        tool.Ifc.get().createIfcCartesianPoint([float(n) for n in position[:, 3][:3]]),
                        tool.Ifc.get().createIfcDirection([float(n) for n in position[:, 2][:3]]),
                        tool.Ifc.get().createIfcDirection([float(n) for n in position[:, 0][:3]]),
                    )
                    items.append(copied_item)
                ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)
            representation.Items = items
            bpy.ops.object.join()
            core.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=self.target,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
                apply_openings=True,
            )

    def join_blender_obj(self):
        for obj in bpy.context.selected_objects:
            if obj == self.target:
                continue
            element = tool.Ifc.get_entity(obj)
            if element:
                ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)
        bpy.ops.object.join()


class OverridePasteBuffer(bpy.types.Operator):
    bl_idname = "bim.override_paste_buffer"
    bl_label = "IFC Paste BIM Objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.view3d.pastebuffer()
        if IfcStore.get_file():
            for obj in context.selected_objects:
                blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=obj)
        return {"FINISHED"}


class OverrideModeSetEdit(bpy.types.Operator):
    bl_description = "Switch from Object mode to Edit mode"
    bl_idname = "bim.override_mode_set_edit"
    bl_label = "IFC Mode Set Edit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        selected_objs = context.selected_objects or ([context.active_object] if context.active_object else [])
        active_obj = context.active_object

        if context.active_object:
            context.active_object.select_set(True)

            element = tool.Ifc.get_entity(context.active_object)
            if element and element.is_a("IfcRelSpaceBoundary"):
                return bpy.ops.bim.enable_editing_boundary_geometry()

        for obj in selected_objs:
            if not obj:
                continue
            if not obj.data:
                obj.select_set(False)
                continue
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            usage_type = tool.Model.get_usage_type(element)
            if usage_type is not None and usage_type not in ("PROFILE", "LAYER3"):
                # Parametric objects shall not be edited as meshes as they
                # can be modified to be incompatible with the parametric
                # constraints.
                obj.select_set(False)
                continue
            representation = tool.Geometry.get_active_representation(obj)
            if not representation:
                continue
            if tool.Blender.Modifier.is_modifier_with_non_editable_path(element):
                obj.select_set(False)
                continue

            is_profile = True
            representation_class = tool.Geometry.get_ifc_representation_class(element, representation)
            if usage_type == "PROFILE":
                operator = lambda: bpy.ops.bim.hotkey(hotkey="A_E")
            elif representation_class and "IfcCircleProfileDef" in representation_class:
                self.report({"INFO"}, "Can't edit Circle Profile Extrusion")
                obj.select_set(False)
                continue
            elif (
                tool.Geometry.is_profile_based(obj.data)
                or usage_type == "LAYER3"
                or tool.Geometry.is_swept_profile(representation)
            ):
                operator = lambda: bpy.ops.bim.hotkey(hotkey="S_E")
            elif tool.Blender.Modifier.is_editing_parameters(obj):
                # This should go BEFORE the modifiers
                self.report({"INFO"}, "Can't edit path while the modifier parameters are being modified")
                obj.select_set(False)
                continue
            elif tool.Blender.Modifier.is_roof(element):
                operator = lambda: bpy.ops.bim.enable_editing_roof_path()
            elif tool.Blender.Modifier.is_railing(element):
                operator = lambda: bpy.ops.bim.enable_editing_railing_path()
            else:
                is_profile = False
            if is_profile:
                if len(context.selected_objects) == 1 and context.active_object == context.selected_objects[0]:
                    tool.Blender.select_and_activate_single_object(context, obj)
                    operator()
                    return {"FINISHED"}
                else:
                    self.report({"INFO"}, "Only a single profile-based representation can be edited at a time.")
                    obj.select_set(False)
                    continue

            if tool.Geometry.is_meshlike(representation):
                tool.Ifc.edit(obj)
                if getattr(element, "HasOpenings", None):
                    # Mesh elements with openings must disable openings
                    # so that you can edit the original topology.
                    core.switch_representation(
                        tool.Ifc,
                        tool.Geometry,
                        obj=obj,
                        representation=representation,
                        should_reload=True,
                        is_global=True,
                        should_sync_changes_first=False,
                        apply_openings=False,
                    )
                tool.Geometry.dissolve_triangulated_edges(obj)
                obj.data.BIMMeshProperties.mesh_checksum = tool.Geometry.get_mesh_checksum(obj.data)
            else:
                obj.select_set(False)
                continue
        if len(selected_objs) > 1 and (
            not context.selected_objects or len(context.selected_objects) != len(selected_objs)
        ):
            # We are trying to edit at least one non-mesh-like object : Display a hint to the user
            self.report({"INFO"}, "Only mesh-compatible representations may be edited concurrently in edit mode.")

        if context.active_object not in context.selected_objects:
            # The active object is non-mesh-like. Set a valid object (or None) as active
            context.view_layer.objects.active = context.selected_objects[0] if context.selected_objects else None
        if context.active_object:
            return tool.Blender.toggle_edit_mode(context)

        # Restore the selection if nothing worked
        for obj in selected_objs:
            obj.select_set(True)
        context.view_layer.objects.active = active_obj
        return {"FINISHED"}

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, is_invoke=True)

    def _invoke(self, context, event):
        if not tool.Ifc.get():
            return tool.Blender.toggle_edit_mode(context)
        return self.execute(context)


class OverrideModeSetObject(bpy.types.Operator):
    bl_idname = "bim.override_mode_set_object"
    bl_label = "IFC Mode Set Object"
    bl_options = {"REGISTER", "UNDO"}
    should_save: bpy.props.BoolProperty(name="Should Save", default=True)

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        for obj in self.edited_objs:
            if self.should_save:
                bpy.ops.bim.update_representation(obj=obj.name, ifc_representation_class="")
                if getattr(tool.Ifc.get_entity(obj), "HasOpenings", False):
                    self.reload_representation(obj)
            else:
                self.reload_representation(obj)
            tool.Ifc.finish_edit(obj)

        for obj in self.unchanged_objs_with_openings:
            self.reload_representation(obj)
            tool.Ifc.finish_edit(obj)
        return {"FINISHED"}

    def reload_representation(self, obj):
        representation = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        core.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
            apply_openings=True,
        )

    def draw(self, context):
        if self.is_valid:
            row = self.layout.row()
            row.prop(self, "should_save")
        else:
            row = self.layout.row()
            row.label(text="No Geometry Found: Object will revert to previous state.")

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, is_invoke=True)

    def _invoke(self, context, event):
        self.is_valid = True
        self.should_save = True

        bpy.ops.object.mode_set(mode="EDIT", toggle=True)

        if not tool.Ifc.get():
            return {"FINISHED"}

        if context.active_object:
            element = tool.Ifc.get_entity(context.active_object)
            if element and element.is_a("IfcRelSpaceBoundary"):
                return bpy.ops.bim.edit_boundary_geometry()

        objs = context.selected_objects or [context.active_object]

        self.edited_objs = []
        self.unchanged_objs_with_openings = []

        for obj in objs:
            if not obj:
                continue

            element = tool.Ifc.get_entity(obj)
            if not element:
                continue

            if tool.Profile.is_editing_profile():
                profile_id = context.scene.BIMProfileProperties.active_profile_id
                if profile_id:
                    profile = tool.Ifc.get().by_id(profile_id)
                    if tool.Ifc.get_object(profile):  # We are editing an arbitrary profile
                        bpy.ops.bim.edit_arbitrary_profile()
                elif tool.Blender.Modifier.is_railing(element):
                    bpy.ops.bim.finish_editing_railing_path()
                elif tool.Blender.Modifier.is_roof(element):
                    bpy.ops.bim.finish_editing_roof_path()
                elif tool.Model.get_usage_type(element) == "PROFILE":
                    bpy.ops.bim.edit_extrusion_axis()
                # if in the process of editing arbitrary profile
                elif context.scene.BIMProfileProperties.active_arbitrary_profile_id:
                    bpy.ops.bim.edit_arbitrary_profile()
                else:
                    bpy.ops.bim.edit_extrusion_profile()
                return self.execute(context)
            elif obj.data.BIMMeshProperties.ifc_definition_id:
                if not tool.Geometry.has_geometric_data(obj):
                    self.is_valid = False
                    self.should_save = False
                representation = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
                if tool.Geometry.is_meshlike(
                    representation
                ) and obj.data.BIMMeshProperties.mesh_checksum != tool.Geometry.get_mesh_checksum(obj.data):
                    self.edited_objs.append(obj)
                elif getattr(element, "HasOpenings", None):
                    self.unchanged_objs_with_openings.append(obj)
                else:
                    tool.Ifc.finish_edit(obj)

        if self.edited_objs:
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)


class FlipObject(bpy.types.Operator):
    bl_idname = "bim.flip_object"
    bl_label = "Flip Object"
    bl_description = "Flip object's local axes, keep the position"
    bl_options = {"REGISTER", "UNDO"}

    flip_local_axes: bpy.props.EnumProperty(
        name="Flip Local Axes", items=(("XY", "XY", ""), ("YZ", "YZ", ""), ("XZ", "XZ", "")), default="XY"
    )

    def execute(self, context):
        for obj in context.selected_objects:
            tool.Geometry.flip_object(obj, self.flip_local_axes)
        return {"FINISHED"}


class EnableEditingRepresentationItems(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_representation_items"
    bl_label = "Enable Editing Representation Items"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object

        props = obj.BIMGeometryProperties
        props.is_editing = True

        props.items.clear()

        if bpy.context.active_object.data and hasattr(bpy.context.active_object.data, "BIMMeshProperties"):
            active_representation_id = bpy.context.active_object.data.BIMMeshProperties.ifc_definition_id
            element = tool.Ifc.get().by_id(active_representation_id)
            if not element.is_a("IfcShapeRepresentation"):
                return
            queue = list(element.Items)
            while queue:
                item = queue.pop()
                if item.is_a("IfcMappedItem"):
                    queue.extend(item.MappingSource.MappedRepresentation.Items)
                else:
                    new = props.items.add()
                    new.name = item.is_a()
                    new.ifc_definition_id = item.id()

                    styles = []
                    for inverse in tool.Ifc.get().get_inverse(item):
                        if inverse.is_a("IfcStyledItem"):
                            styles = inverse.Styles
                            if styles and styles[0].is_a("IfcPresentationStyleAssignment"):
                                styles = styles[0].Styles
                            for style in styles:
                                if style.is_a("IfcSurfaceStyle"):
                                    new.surface_style = style.Name or "Unnamed"
                        elif inverse.is_a("IfcPresentationLayerAssignment"):
                            new.layer = inverse.Name or "Unnamed"


class DisableEditingRepresentationItems(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_representation_items"
    bl_label = "Disable Editing Representation Items"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        obj.BIMGeometryProperties.is_editing = False

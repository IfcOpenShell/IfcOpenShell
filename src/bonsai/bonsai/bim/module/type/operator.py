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

from typing import TYPE_CHECKING

import bpy
import ifcopenshell.api.attribute
import ifcopenshell.api.material
import ifcopenshell.api.type
import ifcopenshell.util.element
import ifcopenshell.util.representation

import bonsai.bim.helper
import bonsai.core.geometry
import bonsai.core.root
import bonsai.core.type as core
import bonsai.tool as tool


class AssignType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_type"
    bl_label = "Assign Type"
    bl_description = "Assign a type to the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    relating_type: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    if TYPE_CHECKING:
        relating_type: int
        related_object: str

    def _execute(self, context):
        if self.relating_type:
            relating_type = self.relating_type
        else:
            assert (obj := context.active_object)
            props = tool.Type.get_object_type_props(obj)
            relating_type = int(props.relating_type)
        relating_type = tool.Ifc.get().by_id(relating_type)
        if self.related_object:
            related_objects = [bpy.data.objects[self.related_object]]
        else:
            related_objects = tool.Blender.get_selected_objects()
        prefs = tool.Blender.get_addon_preferences()

        # Get the active drawing's target view
        active_target_view = None
        drawing_props = context.scene.DocProperties
        if drawing_props.active_drawing_id:
            active_drawing = tool.Ifc.get().by_id(drawing_props.active_drawing_id)
            if active_drawing:
                active_target_view = tool.Drawing.get_drawing_target_view(active_drawing)

        compatible: list[tuple[bpy.types.Object, ifcopenshell.entity_instance]] = []
        skipped_classes: set[str] = set()
        for obj in related_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.is_a("IfcObject"):
                continue
            if not tool.Type.is_relating_type_compatible(element, relating_type):
                skipped_classes.add(element.is_a())
                continue
            compatible.append((obj, element))

        if skipped_classes:
            self.report(
                {"WARNING"},
                f"Skipped {', '.join(sorted(skipped_classes))}: not a valid occurrence for " f"{relating_type.is_a()}.",
            )

        if not compatible:
            self.report({"ERROR"}, f"No selected object can be typed by {relating_type.is_a()}.")
            return {"CANCELLED"}

        for obj, element in compatible:
            core.assign_type(tool.Ifc, tool.Model, tool.Type, element=element, type=relating_type)

            # Switch to the drawing's target view if available
            if active_target_view and element.Representation:
                for rep in element.Representation.Representations:
                    if rep.ContextOfItems.TargetView == active_target_view:
                        bonsai.core.geometry.switch_representation(
                            tool.Ifc,
                            tool.Geometry,
                            obj=obj,
                            representation=rep,
                        )
                        break

            if prefs.occurrence_name_style == "TYPE":
                obj.name = tool.Model.generate_occurrence_name(relating_type, element.is_a())


class UnassignType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_type"
    bl_label = "Unassign Type"
    bl_description = "Unassign a type from the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    if TYPE_CHECKING:
        related_object: str

    @staticmethod
    def _reattach_styles(file: ifcopenshell.file, copied_entities: dict[int, ifcopenshell.entity_instance]) -> None:
        """copy_deep only follows forward references, so IfcStyledItem (an inverse,
        ``StyledByItem``) is not carried onto the copied geometry. Re-create a
        styled item on each copy that points at the same presentation styles as
        the original, so the unmapped occurrence keeps its appearance."""
        for original_id, copied in copied_entities.items():
            original = file.by_id(original_id)
            for styled_item in getattr(original, "StyledByItem", None) or []:
                file.create_entity(
                    "IfcStyledItem",
                    Item=copied,
                    Styles=styled_item.Styles,
                    Name=styled_item.Name,
                )

    @staticmethod
    def unassign_and_unmap(obj: bpy.types.Object) -> None:
        """Unassign the type from ``obj`` and bake a private copy of any mapped
        representation onto it, so the occurrence keeps its geometry, styles, and
        material once the type (the source of all three) is gone."""

        def exclude_callback(attribute):
            return attribute.is_a("IfcProfileDef") and attribute.ProfileName

        file = tool.Ifc.get()
        element = tool.Ifc.get_entity(obj)
        if not element or not element.is_a("IfcObject"):
            return

        # Capture the material inherited from the type before we sever the link,
        # but only if the occurrence has no material of its own to override it.
        own_material = ifcopenshell.util.element.get_material(element, should_inherit=False)
        inherited_material = ifcopenshell.util.element.get_material(element, should_inherit=True)

        ifcopenshell.api.type.unassign_type(file, related_objects=[element])

        if element.Representation:
            new_active_representation = None
            active_representation = tool.Geometry.get_active_representation(obj)
            active_context = active_representation.ContextOfItems
            representations = []
            for representation in element.Representation.Representations:
                resolved_representation = ifcopenshell.util.representation.resolve_representation(representation)
                if representation == resolved_representation:
                    representations.append(representation)
                else:
                    # We must unmap representations, carrying over their styles.
                    copied_entities: dict[int, ifcopenshell.entity_instance] = {}
                    copied_representation = ifcopenshell.util.element.copy_deep(
                        file,
                        resolved_representation,
                        exclude=["IfcGeometricRepresentationContext"],
                        exclude_callback=exclude_callback,
                        copied_entities=copied_entities,
                    )
                    UnassignType._reattach_styles(file, copied_entities)
                    representations.append(copied_representation)
                    if representation.ContextOfItems == active_context:
                        new_active_representation = copied_representation
            element.Representation.Representations = representations

            if new_active_representation:
                bonsai.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=new_active_representation,
                )

        # Bake the inherited material down onto the occurrence now that its type
        # link (and, in the delete-type case, the type itself) is gone. Usages are
        # occurrence-specific and never inherited, so they need no handling here.
        if inherited_material is not None and own_material is None:
            material_type = inherited_material.is_a()
            if material_type not in ("IfcMaterialLayerSetUsage", "IfcMaterialProfileSetUsage"):
                ifcopenshell.api.material.assign_material(
                    file, products=[element], type=material_type, material=inherited_material
                )

    def _execute(self, context):
        if self.related_object:
            related_objects = [bpy.data.objects[self.related_object]]
        else:
            related_objects = tool.Blender.get_selected_objects()

        for obj in related_objects:
            self.unassign_and_unmap(obj)
        return {"FINISHED"}


class EnableEditingType(bpy.types.Operator):
    bl_idname = "bim.enable_editing_type"
    bl_label = "Enable Editing Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        assert (obj := context.active_object)
        props = tool.Type.get_object_type_props(obj)
        props.is_editing_type = True
        props.relating_type_object = None
        return {"FINISHED"}


class DisableEditingType(bpy.types.Operator):
    bl_idname = "bim.disable_editing_type"
    bl_label = "Disable Editing Type"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects[self.obj] if self.obj else context.active_object
        assert obj
        props = tool.Type.get_object_type_props(obj)
        props.is_editing_type = False
        return {"FINISHED"}


class SelectType(bpy.types.Operator):
    bl_idname = "bim.select_type"
    bl_label = "Select Type"
    bl_options = {"REGISTER", "UNDO"}
    relating_type: bpy.props.IntProperty()

    def execute(self, context):

        if self.relating_type:  # if operator button sends a relating_type, the iterator only selects this one type
            element = tool.Ifc.get().by_id(self.relating_type)
            obj = tool.Ifc.get_object(element)
            selected_objs = [obj]
        else:  # else, the iterator selects all the types of all the selected objects
            selected_objs = context.selected_objects
            active_obj = context.active_object
            selected_objs.append(active_obj)  # update selected_objs so the active_obj is at the end of the list

        last_relating_type_obj = None
        for obj in selected_objs:
            element = tool.Ifc.get_entity(obj)
            relating_type = ifcopenshell.util.element.get_type(element)
            if relating_type:
                relating_type_obj = tool.Ifc.get_object(relating_type)
                if relating_type_obj:
                    if relating_type_obj.hide_get():
                        relating_type_obj.hide_set(False)
                    relating_type_obj.select_set(True)
                    last_relating_type_obj = relating_type_obj
            if not element.is_a("IfcTypeObject"):
                obj.select_set(False)

        context.view_layer.objects.active = last_relating_type_obj  # makes the active_obj's type the active object

        return {"FINISHED"}

    def find_collection_in_ifcproject(self, context, collection_name):

        ifc_project_collection = None
        for child in context.view_layer.layer_collection.children:
            if "IfcProject" in child.name:
                ifc_project_collection = child
                break

        if ifc_project_collection:
            collection_in_view_layer = ifc_project_collection.children.get(collection_name)
            return collection_in_view_layer


class SelectSimilarType(bpy.types.Operator):
    bl_idname = "bim.select_similar_type"
    bl_label = "Select Similar Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = tool.Ifc.get()
        objects = bpy.context.selected_objects

        # store relating types to avoid selecting same elements multiple times
        relating_types = set()

        for related_object in objects:
            relating_type = ifcopenshell.util.element.get_type(tool.Ifc.get_entity(related_object))
            if not relating_type:
                # Keep objects without a type selected (retain current selection)
                continue
            relating_types.add(relating_type)

        result = ""
        for relating_type in relating_types:
            related_objects = ifcopenshell.util.element.get_types(relating_type)

            for element in related_objects:
                obj = tool.Ifc.get_object(element)
                if obj and obj in context.visible_objects:
                    obj.select_set(True)

            # copy selection query to clipboard
            related_objects_class = related_objects[0].is_a()
            relating_type_name = relating_type.Name
            if not result:
                result = f'{related_objects_class}, type="{relating_type_name}"'
            else:
                result += f' + {related_objects_class}, type="{relating_type_name}"'
            bpy.context.window_manager.clipboard = result
            self.report({"INFO"}, f"({result}) was copied to the clipboard.")

        return {"FINISHED"}


class SelectTypeObjects(bpy.types.Operator):
    bl_idname = "bim.select_type_objects"
    bl_label = "Select Type Objects"
    bl_options = {"REGISTER", "UNDO"}
    relating_type: bpy.props.StringProperty()

    def execute(self, context):
        self.file = tool.Ifc.get()
        relating_type = bpy.data.objects.get(self.relating_type) if self.relating_type else context.active_object
        at_least_one_selectable_typed_object = False
        for element in ifcopenshell.util.element.get_types(tool.Ifc.get_entity(relating_type)):
            obj = tool.Ifc.get_object(element)
            if obj and obj in context.selectable_objects:
                obj.select_set(True)
                at_least_one_selectable_typed_object = True
        if at_least_one_selectable_typed_object:
            context.active_object.select_set(False)
            context.view_layer.objects.active = context.selected_objects[0]
        else:
            self.report({"INFO"}, "Typed objects can't be selected : They may be hidden or in an excluded collection.")
        return {"FINISHED"}


class RemoveType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_type"
    bl_label = "Delete Type"
    bl_description = (
        "Delete this type. Its occurrences are kept but become untyped.\n\n"
        "SHIFT+Click to also delete every occurrence of this type in the project"
    )
    bl_options = {"REGISTER", "UNDO"}
    element: bpy.props.IntProperty()
    also_delete_instances: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    if TYPE_CHECKING:
        element: int
        also_delete_instances: bool

    @staticmethod
    def _detach_type_material_set(element: ifcopenshell.entity_instance) -> None:
        """Cascade-free removal of the type's IfcMaterialLayerSet / IfcMaterialProfileSet
        association, called just before the type is deleted.

        ``remove_product`` would otherwise route the type's material association
        through ``unassign_material``, which deletes *every* usage of that set
        across the model (documented behaviour, with an upstream TODO calling it
        too aggressive) — stripping the material off the very occurrences we are
        trying to keep. By unhooking the type<->set link by hand here, the type
        has no material at delete time, so that cascade never fires and the set
        plus the occurrences' usages survive intact."""
        file = tool.Ifc.get()
        material = ifcopenshell.util.element.get_material(element, should_inherit=False)
        if not material or material.is_a() not in ("IfcMaterialLayerSet", "IfcMaterialProfileSet"):
            return
        for rel in list(getattr(element, "HasAssociations", None) or []):
            if not (rel.is_a("IfcRelAssociatesMaterial") and rel.RelatingMaterial == material):
                continue
            remaining = [o for o in rel.RelatedObjects if o != element]
            if remaining:
                rel.RelatedObjects = remaining
            else:
                history = rel.OwnerHistory
                file.remove(rel)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)

    def invoke(self, context, event):
        self.also_delete_instances = event.shift
        if self.also_delete_instances:
            element = tool.Ifc.get().by_id(self.element)
            count = len(ifcopenshell.util.element.get_types(element))
            return context.window_manager.invoke_confirm(
                self,
                event,
                title="Delete Type and Occurrences",
                message=f"This will delete the type and all {count} of its occurrences.",
                confirm_text="Delete",
            )
        return self.execute(context)

    def _execute(self, context):
        element = tool.Ifc.get().by_id(self.element)
        occurrences = ifcopenshell.util.element.get_types(element)
        if self.also_delete_instances:
            for occurrence in occurrences:
                occurrence_obj = tool.Ifc.get_object(occurrence)
                if occurrence_obj:
                    tool.Geometry.delete_ifc_object(occurrence_obj)
        else:
            # Keep the occurrences: bake their (previously type-mapped) geometry,
            # styles, and inherited material onto each one so nothing is lost when
            # the type is deleted...
            for occurrence in occurrences:
                occ_obj = tool.Ifc.get_object(occurrence)
                if occ_obj:
                    UnassignType.unassign_and_unmap(occ_obj)
            # ...and keep any layer/profile-set material usages alive across the deletion.
            self._detach_type_material_set(element)
        obj = tool.Ifc.get_object(element)
        if obj:
            tool.Geometry.delete_ifc_object(obj)


class RenameType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.rename_type"
    bl_label = "Rename Type"
    bl_options = {"REGISTER", "UNDO"}
    element: bpy.props.IntProperty()
    name: bpy.props.StringProperty(name="Name")

    def _execute(self, context):
        element = tool.Ifc.get().by_id(self.element)
        obj = tool.Ifc.get_object(element)
        element.Name = self.name
        if obj:
            tool.Root.set_object_name(obj, element)

    def invoke(self, context, event):
        element = tool.Ifc.get().by_id(self.element)
        self.name = element.Name or "Unnamed"
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "name")


class AutoRenameOccurrences(bpy.types.Operator):
    bl_idname = "bim.auto_rename_occurrences"
    bl_label = "Auto Rename Occurrences"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        element_type = tool.Ifc.get_entity(obj)
        if element_type and element_type.is_a("IfcTypeObject"):
            for occurrence in ifcopenshell.util.element.get_types(element_type):
                obj = tool.Ifc.get_object(occurrence)
                occurrence.Name = tool.Model.generate_occurrence_name(element_type, occurrence.is_a())
                if obj:
                    tool.Root.set_object_name(obj, occurrence)
        return {"FINISHED"}


class DuplicateType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_type"
    bl_label = "Duplicate Type"
    bl_options = {"REGISTER", "UNDO"}
    element: bpy.props.IntProperty()
    name: bpy.props.StringProperty(name="Name")
    description: bpy.props.StringProperty(name="Description")
    assign_selected_objects: bpy.props.BoolProperty(default=False)

    if TYPE_CHECKING:
        element: int
        name: str
        description: str
        assign_selected_objects: bool

    def _execute(self, context):
        element = tool.Ifc.get().by_id(self.element)
        obj = tool.Ifc.get_object(element)
        if not obj:
            return {"FINISHED"}
        new_obj = obj.copy()
        if obj.data:
            new_obj.data = obj.data.copy()
        new = bonsai.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new_obj)

        # Apply the name and description from the dialog
        new.Name = self.name
        if self.description:
            new.Description = self.description

        # Update the Blender object name to match the IFC element name
        tool.Root.set_object_name(new_obj, new)

        bpy.ops.bim.load_type_thumbnails()

        # Assign selected objects to the new type if requested
        if self.assign_selected_objects:
            selected_objects = tool.Blender.get_selected_objects()
            prefs = tool.Blender.get_addon_preferences()
            skipped_classes: set[str] = set()
            for selected_obj in selected_objects:
                selected_element = tool.Ifc.get_entity(selected_obj)
                if not selected_element or not selected_element.is_a("IfcObject"):
                    continue
                if not tool.Type.is_relating_type_compatible(selected_element, new):
                    skipped_classes.add(selected_element.is_a())
                    continue
                core.assign_type(tool.Ifc, tool.Model, tool.Type, element=selected_element, type=new)
                if prefs.occurrence_name_style == "TYPE":
                    selected_obj.name = tool.Model.generate_occurrence_name(new, selected_element.is_a())
            if skipped_classes:
                self.report(
                    {"WARNING"},
                    f"Skipped {', '.join(sorted(skipped_classes))}: not a valid occurrence for " f"{new.is_a()}.",
                )

        if obj in context.selectable_objects:
            tool.Blender.select_and_activate_single_object(context, new_obj)
        else:
            self.report({"INFO"}, "Type object can't be selected : It may be hidden or in an excluded collection.")

        props = tool.Model.get_model_props()

        ifc_class = new.is_a()
        # Set duplicated type as active in current tool.
        if ifc_class in (i[0] for i in (bonsai.bim.helper.get_enum_items(props, "ifc_class", context) or ()) if i):
            props.ifc_class = new.is_a()
            # Guards the same enum/ifc_class race handled in
            # bim/handler.py:update_bim_tool_props (see 233cc344fa).
            try:
                props.relating_type_id = str(tool.Blender.get_ifc_definition_id(new_obj))
            except TypeError:
                pass
        return {"FINISHED"}

    def invoke(self, context, event):
        element = tool.Ifc.get().by_id(self.element)
        self.name = (element.Name or "Unnamed") + " Copy"
        self.description = element.Description or ""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "name")
        self.layout.prop(self, "description")
        selected_objects = tool.Blender.get_selected_objects()
        ifc_objects = [
            obj for obj in selected_objects if tool.Ifc.get_entity(obj) and tool.Ifc.get_entity(obj).is_a("IfcObject")
        ]
        if ifc_objects:
            self.layout.prop(
                self, "assign_selected_objects", text=f"Assign {len(ifc_objects)} Selected Object(s) to New Type"
            )


class EnableEditingTypeAttributes(bpy.types.Operator):
    bl_idname = "bim.enable_editing_type_attributes"
    bl_label = "Enable Editing Type Attributes"
    bl_description = "Enable editing the attributes of the relating type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        element = tool.Ifc.get_entity(obj)
        if not element:
            return {"CANCELLED"}

        element_type = ifcopenshell.util.element.get_type(element)
        if not element_type:
            return {"CANCELLED"}

        props = tool.Type.get_object_type_props(obj)
        props.type_attributes.clear()

        bonsai.bim.helper.import_attributes(element_type, props.type_attributes)
        props.is_editing_type_attributes = True
        return {"FINISHED"}


class DisableEditingTypeAttributes(bpy.types.Operator):
    bl_idname = "bim.disable_editing_type_attributes"
    bl_label = "Disable Editing Type Attributes"
    bl_description = "Disable editing the attributes of the relating type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Type.get_object_type_props(obj)
        props.type_attributes.clear()
        props.property_unset("is_editing_type_attributes")
        return {"FINISHED"}


class EditTypeAttributes(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_type_attributes"
    bl_label = "Edit Type Attributes"
    bl_description = "Save the changes to the relating type's attributes"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        element = tool.Ifc.get_entity(obj)
        if not element:
            return {"CANCELLED"}

        element_type = ifcopenshell.util.element.get_type(element)
        if not element_type:
            return {"CANCELLED"}

        props = tool.Type.get_object_type_props(obj)
        attributes = bonsai.bim.helper.export_attributes(props.type_attributes)

        ifcopenshell.api.attribute.edit_attributes(tool.Ifc.get(), product=element_type, attributes=attributes)

        type_obj = tool.Ifc.get_object(element_type)
        if type_obj:
            tool.Root.set_object_name(type_obj, element_type)

        bpy.ops.bim.disable_editing_type_attributes()

        return {"FINISHED"}

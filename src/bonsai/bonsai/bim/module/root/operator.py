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

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.schema
import ifcopenshell.util.element
import ifcopenshell.util.type
import bonsai.bim.handler
import bonsai.core.root as core
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import get_enum_items


class EnableReassignClass(bpy.types.Operator):
    bl_idname = "bim.enable_reassign_class"
    bl_label = "Enable Reassign IFC Class"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        self.file = IfcStore.get_file()
        ifc_class = obj.name.split("/")[0]
        context.active_object.BIMObjectProperties.is_reassigning_class = True
        ifc_products = [
            "IfcElement",
            "IfcElementType",
            "IfcSpatialElement",
            "IfcGroup",
            "IfcStructural",
            "IfcPositioningElement",
            "IfcContext",
            "IfcAnnotation",
            "IfcRelSpaceBoundary",
        ]
        for ifc_product in ifc_products:
            if ifcopenshell.util.schema.is_a(IfcStore.get_schema().declaration_by_name(ifc_class), ifc_product):
                context.scene.BIMRootProperties.ifc_product = ifc_product
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        context.scene.BIMRootProperties.ifc_class = element.is_a()
        context.scene.BIMRootProperties.relating_class_object = None
        if hasattr(element, "PredefinedType"):
            if element.PredefinedType:
                context.scene.BIMRootProperties.ifc_predefined_type = element.PredefinedType
            userdefined_type = ifcopenshell.util.element.get_predefined_type(element)
            context.scene.BIMRootProperties.ifc_userdefined_type = userdefined_type or ""
        return {"FINISHED"}


class DisableReassignClass(bpy.types.Operator):
    bl_idname = "bim.disable_reassign_class"
    bl_label = "Disable Reassign IFC Class"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.active_object.BIMObjectProperties.is_reassigning_class = False
        return {"FINISHED"}


class ReassignClass(bpy.types.Operator):
    bl_idname = "bim.reassign_class"
    bl_label = "Reassign IFC Class"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        if self.obj:
            objects = [bpy.data.objects.get(self.obj)]
        else:
            objects = set(context.selected_objects + [context.active_object])
        self.file = IfcStore.get_file()
        predefined_type = context.scene.BIMRootProperties.ifc_predefined_type
        if predefined_type == "USERDEFINED":
            predefined_type = context.scene.BIMRootProperties.ifc_userdefined_type

        # NOTE: root.reassign_class
        # automatically will reassign class for other occurrences of the type
        # so we need to run it only for the types or non-typed elements
        elements_to_reassign = set()
        # need to update blender object name
        # for all elements that were changed in the process
        elements_to_update = set()
        for obj in objects:
            obj.BIMObjectProperties.is_reassigning_class = False
            element = tool.Ifc.get_entity(obj)
            if element.is_a("IfcTypeObject"):
                elements_to_reassign.add(element)
                elements_to_update.update(ifcopenshell.util.element.get_types(element))
                continue

            # check if element is typed
            element_type = ifcopenshell.util.element.get_type(element)
            if element_type:
                elements_to_reassign.add(element_type)
                elements_to_update.update(ifcopenshell.util.element.get_types(element_type))
                continue

            # non-typed element
            elements_to_reassign.add(element)

        # store elements to objects to update later as elements will get invalid
        # after class reassignment
        elements_to_update = elements_to_update | elements_to_reassign
        objects_to_update = set(o for e in elements_to_update if (o := tool.Ifc.get_object(e)))

        base_class = context.scene.BIMRootProperties.ifc_class
        if context.scene.BIMRootProperties.ifc_product == "IfcElementType":
            type_class = base_class
            occurrence_classes = ifcopenshell.util.type.get_applicable_entities(type_class)
            occurrence_class = None if len(occurrence_classes) == 0 else occurrence_classes[0]
        else:
            occurrence_class = base_class
            type_classes = ifcopenshell.util.type.get_applicable_types(occurrence_class)
            type_class = None if len(type_classes) == 0 else type_classes[0]

        reassigned_elements = set()
        for element in elements_to_reassign:
            ifc_class = type_class if element.is_a("IfcTypeObject") else occurrence_class
            if ifc_class is None:
                self.report(
                    {"ERROR"},
                    f"Couldn't find valid class for reassigning element of class {element.is_a()} based on class {base_class}",
                )
                return {"CANCELLED"}

            element = ifcopenshell.api.run(
                "root.reassign_class",
                self.file,
                product=element,
                ifc_class=ifc_class,
                predefined_type=predefined_type,
            )
            reassigned_elements.add(element)

        for obj in objects_to_update:
            obj.name = tool.Loader.get_name(tool.Ifc.get_entity(obj))
        return {"FINISHED"}


class AssignClass(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_class"
    bl_label = "Assign IFC Class"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Assign the IFC Class to the selected objects"
    obj: bpy.props.StringProperty()
    ifc_class: bpy.props.StringProperty()
    predefined_type: bpy.props.StringProperty()
    userdefined_type: bpy.props.StringProperty()
    context_id: bpy.props.IntProperty()
    should_add_representation: bpy.props.BoolProperty(default=True)
    ifc_representation_class: bpy.props.StringProperty()

    def _execute(self, context):
        props = context.scene.BIMRootProperties
        objects: list[bpy.types.Object] = []
        if self.obj:
            objects = [bpy.data.objects[self.obj]]
        elif objects := context.selected_objects:
            pass
        elif obj := context.active_object:
            objects = [obj]

        if not objects:
            self.report({"INFO"}, "No objects selected.")
            return

        ifc_class = self.ifc_class or props.ifc_class
        predefined_type = self.userdefined_type if self.predefined_type == "USERDEFINED" else self.predefined_type
        ifc_context = self.context_id
        if not ifc_context and get_enum_items(props, "contexts", context):
            ifc_context = int(props.contexts or "0") or None
        if ifc_context:
            ifc_context = tool.Ifc.get().by_id(ifc_context)
        active_object = context.active_object
        for obj in objects:
            if obj.mode != "OBJECT":
                self.report({"ERROR"}, "Object must be in OBJECT mode to assign class")
                continue
            core.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=ifc_class,
                predefined_type=predefined_type,
                should_add_representation=self.should_add_representation,
                context=ifc_context,
                ifc_representation_class=self.ifc_representation_class,
            )
        context.view_layer.objects.active = active_object


class UnlinkObject(bpy.types.Operator):
    bl_idname = "bim.unlink_object"
    bl_label = "Unlink Object"
    bl_description = (
        "Unlink Blender object from it's linked IFC element.\n\n"
        "You can either remove element the blender object is linked to from IFC or keep it. "
        "Note that keeping the unlinked element in IFC might lead to unpredictable issues "
        "and should be used only by advanced users"
    )
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty(name="Object Name")
    should_delete: bpy.props.BoolProperty(name="Delete IFC Element", default=True)
    skip_invoke: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        if self.obj:
            objects = [bpy.data.objects.get(self.obj)]
        else:
            objects = context.selected_objects

        objects: list[bpy.types.Object]
        for obj in objects:
            was_active_object = obj == context.active_object

            tool.Ifc.finish_edit(obj)

            element = tool.Ifc.get_entity(obj)
            if element and self.should_delete:
                object_name = obj.name

                # Copy object, so it won't be removed by `delete_ifc_object`
                obj_copy = obj.copy()
                if obj.data:
                    obj_copy.data = obj.data.copy()

                    # prevent unlinking materials that might be used elsewhere
                    replacements: dict[bpy.types.Material, bpy.types.Material] = dict()
                    for material_slot in obj_copy.material_slots:
                        material = material_slot.material
                        if material is None:
                            continue

                        if material in replacements:
                            material_replacement = replacements[material]

                        # no need to copy non-ifc materials as unlinking won't do anything to them
                        elif tool.Ifc.get_entity(material) is None and tool.Style.get_style(material) is None:
                            replacements[material] = material
                            continue

                        else:
                            material_replacement = material.copy()
                            replacements[material] = material_replacement

                        material_slot.material = material_replacement

                tool.Geometry.delete_ifc_object(obj)

                obj = obj_copy
                obj.name = object_name
            elif element:
                tool.Ifc.unlink(element)

            tool.Root.unlink_object(obj)
            for collection in obj.users_collection:
                # Reset collection because its original collection may be removed too.
                collection.objects.unlink(obj)
            bpy.context.scene.collection.objects.link(obj)

            if was_active_object:
                tool.Blender.set_active_object(obj)
        return {"FINISHED"}

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "should_delete")

    def invoke(self, context, event):
        if self.skip_invoke:
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self)


class CopyClass(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_class"
    bl_label = "Copy Class"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objects:
            core.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=obj)
        bonsai.bim.handler.refresh_ui_data()

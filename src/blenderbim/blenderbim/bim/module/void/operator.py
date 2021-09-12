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
import ifcopenshell.api
import ifcopenshell.util.representation
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.void.data import Data


class AddOpening(bpy.types.Operator):
    bl_idname = "bim.add_opening"
    bl_label = "Add Opening"
    bl_options = {"REGISTER", "UNDO"}
    opening: bpy.props.StringProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = context.scene.objects.get(self.obj, context.active_object)
        opening = bpy.data.objects.get(self.opening)
        if opening is None:
            return {"FINISHED"}
        opening.display_type = "WIRE"
        if not opening.BIMObjectProperties.ifc_definition_id:
            body_context = ifcopenshell.util.representation.get_context(IfcStore.get_file(), "Model", "Body")
            if not body_context:
                return {"FINISHED"}
            bpy.ops.bim.assign_class(obj=opening.name, ifc_class="IfcOpeningElement", context_id=body_context.id())

        self.file = IfcStore.get_file()
        element_id = obj.BIMObjectProperties.ifc_definition_id
        ifcopenshell.api.run(
            "void.add_opening",
            self.file,
            **{
                "opening": self.file.by_id(opening.BIMObjectProperties.ifc_definition_id),
                "element": self.file.by_id(element_id),
            },
        )
        Data.load(IfcStore.get_file(), element_id)

        has_modifier = False

        for modifier in obj.modifiers:
            if modifier.type == "BOOLEAN" and modifier.object and modifier.object == opening:
                has_modifier = True
                break

        if not has_modifier:
            modifier = obj.modifiers.new("IfcOpeningElement", "BOOLEAN")
            modifier.operation = "DIFFERENCE"
            modifier.object = opening
            modifier.solver = "EXACT"
            modifier.use_self = True
        return {"FINISHED"}


class RemoveOpening(bpy.types.Operator):
    bl_idname = "bim.remove_opening"
    bl_label = "Remove Opening"
    bl_options = {"REGISTER", "UNDO"}
    opening_id: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        is_modifier_removed = False
        for modifier in obj.modifiers:
            if modifier.type != "BOOLEAN":
                continue
            if modifier.object and modifier.object.BIMObjectProperties.ifc_definition_id == self.opening_id:
                is_modifier_removed = True
                obj.modifiers.remove(modifier)
                break

        opening = IfcStore.get_element(self.opening_id)
        opening.name = "/".join(opening.name.split("/")[1:])
        IfcStore.unlink_element(obj=opening)

        ifcopenshell.api.run("void.remove_opening", self.file, **{"opening": self.file.by_id(self.opening_id)})

        if not is_modifier_removed:
            bpy.ops.bim.switch_representation(
                ifc_definition_id=obj.data.BIMMeshProperties.ifc_definition_id,
                should_reload=True,
                should_switch_all_meshes=True,
            )

        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class AddFilling(bpy.types.Operator):
    bl_idname = "bim.add_filling"
    bl_label = "Add Filling"
    bl_options = {"REGISTER", "UNDO"}
    opening: bpy.props.StringProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = context.scene.objects.get(self.obj, context.active_object)
        opening = context.scene.objects.get(self.opening, context.scene.VoidProperties.desired_opening)
        if opening is None:
            return {"FINISHED"}
        self.file = IfcStore.get_file()
        element_id = obj.BIMObjectProperties.ifc_definition_id
        ifcopenshell.api.run(
            "void.add_filling",
            self.file,
            **{
                "opening": self.file.by_id(opening.BIMObjectProperties.ifc_definition_id),
                "element": self.file.by_id(element_id),
            },
        )
        Data.load(IfcStore.get_file(), element_id)
        return {"FINISHED"}


class RemoveFilling(bpy.types.Operator):
    bl_idname = "bim.remove_filling"
    bl_label = "Remove Filling"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "void.remove_filling", self.file, **{"element": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)}
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class ToggleOpeningVisibility(bpy.types.Operator):
    bl_idname = "bim.toggle_opening_visibility"
    bl_label = "Toggle Opening Visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for project in [c for c in context.view_layer.layer_collection.children if "IfcProject" in c.name]:
            for collection in [c for c in project.children if "IfcOpeningElements" in c.name]:
                collection.hide_viewport = not collection.hide_viewport
        return {"FINISHED"}


class ToggleDecompositionParenting(bpy.types.Operator):
    bl_idname = "bim.toggle_decomposition_parenting"
    bl_label = "Toggle Decomposition Parenting"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        is_parenting = None

        self.decompositions = {}
        self.load_decompositions(obj)

        for parent, children in self.decompositions.items():
            bpy.ops.bim.dynamically_void_product(obj=parent.name)
            for child in children:
                bpy.ops.bim.dynamically_void_product(obj=child.name)
                if is_parenting is None:
                    is_parenting = not bool(child.parent)

                if is_parenting:
                    child.parent = parent
                    child.matrix_parent_inverse = parent.matrix_world.inverted()
                else:
                    parent_matrix_world = child.matrix_world.copy()
                    child.parent = None
                    child.matrix_world = parent_matrix_world

        return {"FINISHED"}

    def load_decompositions(self, parent_obj):
        element = self.file.by_id(parent_obj.BIMObjectProperties.ifc_definition_id)
        for rel in self.file.get_inverse(element):
            if rel.is_a("IfcRelDecomposes"):
                if rel[4] != element:
                    continue
                if isinstance(rel[5], tuple):
                    for related_object in rel[5]:
                        self.add_decomposition(parent_obj, related_object)
                else:
                    self.add_decomposition(parent_obj, rel[5])
            elif rel.is_a("IfcRelFillsElement"):
                if rel.RelatingOpeningElement != element:
                    continue
                self.add_decomposition(parent_obj, rel.RelatedBuildingElement)

    def add_decomposition(self, parent_obj, child_element):
        child_obj = IfcStore.get_element(child_element.id())
        if child_obj:
            self.decompositions.setdefault(parent_obj, []).append(child_obj)
            self.load_decompositions(child_obj)

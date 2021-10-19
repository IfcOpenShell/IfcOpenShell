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
import blenderbim.tool as tool
import blenderbim.core.geometry
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
        self.file = IfcStore.get_file()
        obj = context.scene.objects.get(self.obj, context.active_object)
        if obj is None:
            return {"FINISHED"}
        element_id = obj.BIMObjectProperties.ifc_definition_id
        if not element_id:
            return {"FINISHED"}
        element = self.file.by_id(element_id)
        if element.is_a("IfcOpeningElement"):
            self.report({"WARNING"}, "An IfcOpeningElement can't be voided")
            return {"FINISHED"}

        opening = bpy.data.objects.get(self.opening)
        if opening is None:
            return {"FINISHED"}
        opening.display_type = "WIRE"
        if not opening.BIMObjectProperties.ifc_definition_id:
            body_context = ifcopenshell.util.representation.get_context(IfcStore.get_file(), "Model", "Body")
            if not body_context:
                return {"FINISHED"}
            bpy.ops.bim.assign_class(obj=opening.name, ifc_class="IfcOpeningElement", context_id=body_context.id())

        # If the IfcOpeningElement aleady voids another object, remove the boolean modifier
        opening_element = self.file.by_id(opening.BIMObjectProperties.ifc_definition_id)
        if opening_element.VoidsElements:
            other_obj = IfcStore.get_element(opening_element.VoidsElements[0].RelatingBuildingElement.id())
            try:
                modifier = next(m for m in other_obj.modifiers if m.type == "BOOLEAN" and m.object == opening)
                other_obj.modifiers.remove(modifier)
            except StopIteration:
                pass

        ifcopenshell.api.run(
            "void.add_opening",
            self.file,
            **{
                "opening": opening_element,
                "element": element,
            },
        )
        Data.load(self.file, element_id)

        try:
            modifier = next(m for m in obj.modifiers if m.type == "BOOLEAN" and m.object == opening)
        except StopIteration:
            modifier = obj.modifiers.new("IfcOpeningElement", "BOOLEAN")
            modifier.object = opening
        finally:
            modifier.operation = "DIFFERENCE"
            modifier.solver = "EXACT"
            modifier.use_self = True
            modifier.operand_type = "OBJECT"

        context.view_layer.objects.active = obj
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
            blenderbim.core.geometry.switch_representation(
                tool.Geometry,
                obj=obj,
                representation=tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id),
                should_reload=True,
                enable_dynamic_voids=False,
                is_global=True,
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
        opening_id = opening.BIMObjectProperties.ifc_definition_id
        if not element_id or not opening_id or element_id == opening_id:
            return {"FINISHED"}
        ifcopenshell.api.run(
            "void.add_filling",
            self.file,
            **{
                "opening": self.file.by_id(opening_id),
                "element": self.file.by_id(element_id),
            },
        )
        Data.load(self.file, element_id)
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
        if not obj:
            return {"FINISHED"}
        self.file = IfcStore.get_file()
        element_id = obj.BIMObjectProperties.ifc_definition_id
        if not element_id:
            return {"FINISHED"}
        ifcopenshell.api.run("void.remove_filling", self.file, **{"element": self.file.by_id(element_id)})
        Data.load(self.file, element_id)
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

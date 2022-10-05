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


class AddOpening(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_opening"
    bl_label = "Add Opening"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        if len(context.selected_objects) != 2:
            return {"FINISHED"}
        obj1, obj2 = context.selected_objects
        element1 = tool.Ifc.get_entity(obj1)
        element2 = tool.Ifc.get_entity(obj2)
        if type(element1) == type(element2):
            return {"FINISHED"}
        if element2 and not element1:
            obj1, obj2 = obj2, obj1
            element1, element2 = element2, element1
        if element1.is_a("IfcOpeningElement"):
            return {"FINISHED"}
        if obj2 not in [o.obj for o in props.openings]:
            return {"FINISHED"}
        if not obj1.data or not hasattr(obj1.data, "BIMMeshProperties"):
            return {"FINISHED"}

        if tool.Ifc.is_moved(obj1):
            blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj1)

        has_visible_openings = False
        for opening in [r.RelatedOpeningElement for r in element1.HasOpenings]:
            if tool.Ifc.get_object(opening):
                has_visible_openings = True
                break

        body_context = ifcopenshell.util.representation.get_context(IfcStore.get_file(), "Model", "Body")
        element2 = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj2,
            ifc_class="IfcOpeningElement",
            should_add_representation=True,
            context=body_context,
        )
        ifcopenshell.api.run("void.add_opening", tool.Ifc.get(), opening=element2, element=element1)

        representation = tool.Ifc.get().by_id(obj1.data.BIMMeshProperties.ifc_definition_id)
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj1,
            representation=representation,
            should_reload=True,
            enable_dynamic_voids=False,
            is_global=True,
            should_sync_changes_first=False,
        )
        Data.load(tool.Ifc.get(), element1.id())

        if not has_visible_openings:
            tool.Ifc.unlink(obj=obj2)
            bpy.data.objects.remove(obj2)

        context.view_layer.objects.active = obj1
        return {"FINISHED"}


class RemoveOpening(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_opening"
    bl_label = "Remove Opening"
    bl_options = {"REGISTER", "UNDO"}
    opening_id: bpy.props.IntProperty()

    def _execute(self, context):
        opening = tool.Ifc.get().by_id(self.opening_id)
        opening_obj = tool.Ifc.get_object(opening)
        element = opening.VoidsElements[0].RelatingBuildingElement
        obj = tool.Ifc.get_object(element)

        if opening_obj:
            opening_obj.name = "/".join(opening_obj.name.split("/")[1:])
            IfcStore.unlink_element(obj=opening_obj)

        ifcopenshell.api.run("void.remove_opening", tool.Ifc.get(), opening=opening)

        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id),
            should_reload=True,
            enable_dynamic_voids=False,
            is_global=True,
            should_sync_changes_first=False,
        )

        tool.Geometry.clear_cache(element)
        Data.load(tool.Ifc.get(), obj.BIMObjectProperties.ifc_definition_id)
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

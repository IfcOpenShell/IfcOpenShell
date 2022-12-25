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
            if (
                element1
                and element2
                and not element1.is_a("IfcOpeningElement")
                and not element2.is_a("IfcOpeningElement")
            ):
                if element1.is_a("IfcWindow") or element1.is_a("IfcDoor"):
                    obj1, obj2 = obj2, obj1
                bpy.ops.bim.add_filled_opening(voided_obj=obj1.name, filling_obj=obj2.name)
            return {"FINISHED"}
        if element2 and not element1:
            obj1, obj2 = obj2, obj1
            element1, element2 = element2, element1
        if element1.is_a("IfcOpeningElement"):
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
            is_global=True,
            should_sync_changes_first=False,
        )

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
            is_global=True,
            should_sync_changes_first=False,
        )

        tool.Geometry.clear_cache(element)
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
            "void.add_filling", self.file, opening=self.file.by_id(opening_id), element=self.file.by_id(element_id)
        )
        return {"FINISHED"}


class RemoveFilling(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_filling"
    bl_label = "Remove Filling"
    bl_options = {"REGISTER", "UNDO"}
    filling: bpy.props.IntProperty()

    def _execute(self, context):
        filling = tool.Ifc.get().by_id(self.filling)
        filling_obj = tool.Ifc.get_object(filling)
        for rel in filling.FillsVoids:
            bpy.ops.bim.remove_opening(opening_id=rel.RelatingOpeningElement.id())
        ifcopenshell.api.run("void.remove_filling", tool.Ifc.get(), element=filling)
        return {"FINISHED"}


class SelectDecomposition(bpy.types.Operator):
    bl_idname = "bim.select_decomposition"
    bl_label = "Select Decomposition"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            for subelement in ifcopenshell.util.element.get_decomposition(element):
                subobj = tool.Ifc.get_object(subelement)
                if subobj:
                    subobj.select_set(True)
        return {"FINISHED"}

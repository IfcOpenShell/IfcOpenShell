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
import blenderbim.core.root
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.model.opening import FilledOpeningGenerator


class AddOpening(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_opening"
    bl_label = "Add Opening"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Adds an opening to an element.\n" "Need to select two elements, order of selection is not important"
    )

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) < 2:
            cls.poll_message_set("Select openings and a target element")
        return True

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        selected_objects = context.selected_objects
        target_object = selected_objects[0]

        opening_objects = [obj for obj in selected_objects if obj != target_object]

        for opening_obj in opening_objects:
            element1 = tool.Ifc.get_entity(target_object)
            obj1 = target_object
            element2 = tool.Ifc.get_entity(opening_obj)
            obj2 = opening_obj

            if not element1 and not element2:
                return {"FINISHED"}  # Both are not IFC objects.

            if element1 and element2:
                if element1.is_a("IfcOpeningElement") and element2.is_a("IfcOpeningElement"):
                    self.report({"INFO"}, "You can't add an opening to another opening.")
                    continue
                elif not element1.is_a("IfcOpeningElement") and not element2.is_a("IfcOpeningElement"):
                    if element1.is_a("IfcWindow") or element1.is_a("IfcDoor"):  # Add a fill to an element.
                        obj1, obj2 = obj2, obj1
                    FilledOpeningGenerator().generate(obj2, obj1, target=obj2.matrix_world.translation)
                    continue
                elif element1.is_a("IfcOpeningElement") or element2.is_a("IfcOpeningElement"):
                    if element1.is_a("IfcOpeningElement"):  # Reassign an opening to another element.
                        obj1, obj2 = obj2, obj1
                        element1, element2 = element2, element1

            if element2 and not element1:
                obj1, obj2 = obj2, obj1
                element1, element2 = element2, element1

            if element1.is_a("IfcOpeningElement"):
                self.report({"INFO"}, "You can't add an opening to another opening.")
                continue

            if not hasattr(element1, "HasOpenings"):
                self.report({"INFO"}, f"An {element1.is_a()} is not allowed to have an opening.")
                continue

            if tool.Ifc.is_moved(obj1):
                blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj1)

            has_visible_openings = False
            for opening in [r.RelatedOpeningElement for r in element1.HasOpenings]:
                if tool.Ifc.get_object(opening):
                    has_visible_openings = True
                    break

            body_context = ifcopenshell.util.representation.get_context(IfcStore.get_file(), "Model", "Body")
            if not element2:
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

            if tool.Ifc.is_moved(obj2):
                blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj2)

            voided_objs = [obj1]
            for subelement in ifcopenshell.util.element.get_decomposition(element1):
                subobj = tool.Ifc.get_object(subelement)
                if subobj:
                    voided_objs.append(subobj)

            for voided_obj in voided_objs:
                if voided_obj.data:
                    representation = tool.Ifc.get().by_id(voided_obj.data.BIMMeshProperties.ifc_definition_id)
                    blenderbim.core.geometry.switch_representation(
                        tool.Ifc,
                        tool.Geometry,
                        obj=voided_obj,
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
            tool.Ifc.unlink(obj=opening_obj)

        ifcopenshell.api.run("void.remove_opening", tool.Ifc.get(), opening=opening)

        decomposed_building_elements = set([element])
        decomposed_building_elements.update(ifcopenshell.util.element.get_decomposition(element))

        for building_element in decomposed_building_elements:
            building_obj = tool.Ifc.get_object(building_element)
            if building_obj and building_obj.data:
                representation = tool.Geometry.get_active_representation(building_obj)
                blenderbim.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=building_obj,
                    representation=representation,
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


class BooleansMarkAsManual(bpy.types.Operator):
    bl_idname = "bim.booleans_mark_as_manual"
    bl_label = "Mark Booleans as Manual"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "\nMark all booleans in object's current representations as manual.\n"
        "Manual booleans will be preserved until they are removed explicitly"
    )
    mark_as_manual: bpy.props.BoolProperty(name="Mark as Manual", default=True)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if (
            obj
            and tool.Ifc.get_entity(obj)
            and hasattr(obj.data, "BIMMeshProperties")
            and obj.data.BIMMeshProperties.ifc_definition_id
        ):
            return True
        cls.poll_message_set("Need to select IFC element with representation")
        return False

    def execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        representation = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        booleans = tool.Model.get_booleans(representation=representation)

        if self.mark_as_manual:
            tool.Model.mark_manual_booleans(element, booleans)
        else:
            tool.Model.unmark_manual_booleans(element, [b.id() for b in booleans])

        self.report(
            {"INFO"}, f"{len(booleans)} booleans were marked as {'manual' if self.mark_as_manual else 'automatic'}"
        )
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}

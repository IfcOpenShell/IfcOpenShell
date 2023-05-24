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
import ifcopenshell
import ifcopenshell.util.element
import blenderbim.tool as tool
import blenderbim.core.aggregate as core
import blenderbim.core.spatial
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class BIM_OT_assign_object(bpy.types.Operator, Operator):
    """Create aggregation relationship between two ifc elements"""

    bl_idname = "bim.assign_object"
    bl_label = "Assign Object"
    bl_options = {"REGISTER", "UNDO"}
    relating_object: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

    def _execute(self, context):
        for obj in bpy.context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            relating_obj = tool.Ifc.get_object(tool.Ifc.get().by_id(self.relating_object))
            result = core.assign_object(
                tool.Ifc,
                tool.Aggregate,
                tool.Collector,
                relating_obj=relating_obj,
                related_obj=obj,
            )
            if not result:
                self.report({"ERROR"}, f"Objects {relating_obj} and {obj} cannot be aggregated")

        return {"FINISHED"}


class BIM_OT_unassign_object(bpy.types.Operator, Operator):
    """Remove aggregation relationship between two ifc elements"""

    bl_idname = "bim.unassign_object"
    bl_label = "Unassign Object"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        for obj in bpy.context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            aggregate = ifcopenshell.util.element.get_aggregate(element)
            if not aggregate:
                continue
            core.unassign_object(
                tool.Ifc,
                tool.Aggregate,
                tool.Collector,
                relating_obj=tool.Ifc.get_object(aggregate),
                related_obj=tool.Ifc.get_object(element),
            )


class BIM_OT_enable_editing_aggregate(bpy.types.Operator, Operator):
    """Enable editing aggregation relationship"""

    bl_idname = "bim.enable_editing_aggregate"
    bl_label = "Enable Editing Aggregate"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_aggregate(tool.Aggregate, obj=context.active_object)


class BIM_OT_disable_editing_aggregate(bpy.types.Operator, Operator):
    """Disable editing aggregation relationship"""

    bl_idname = "bim.disable_editing_aggregate"
    bl_label = "Disable Editing Aggregate"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_aggregate(tool.Aggregate, obj=context.active_object)


class BIM_OT_add_aggregate(bpy.types.Operator, tool.Ifc.Operator):
    """Add aggregate to IFC element"""

    bl_idname = "bim.add_aggregate"
    bl_label = "Add Aggregate"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    ifc_class: bpy.props.StringProperty(name="IFC Class", default="IfcElementAssembly")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.prop(self, "ifc_class")

    def _execute(self, context):
        try:
            ifc_class = tool.Ifc.schema().declaration_by_name(self.ifc_class).name()
        except:
            return
        aggregate = self.create_aggregate(context, ifc_class)

        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue

            tool.Collector.sync(obj)
            current_aggregate = ifcopenshell.util.element.get_aggregate(element)
            current_container = ifcopenshell.util.element.get_container(element)
            if current_aggregate:
                core.assign_object(
                    tool.Ifc,
                    tool.Aggregate,
                    tool.Collector,
                    relating_obj=tool.Ifc.get_object(current_aggregate),
                    related_obj=aggregate,
                )
            elif current_container:
                blenderbim.core.spatial.assign_container(
                    tool.Ifc,
                    tool.Collector,
                    tool.Spatial,
                    structure_obj=tool.Ifc.get_object(current_container),
                    element_obj=aggregate,
                )
            core.assign_object(tool.Ifc, tool.Aggregate, tool.Collector, relating_obj=aggregate, related_obj=obj)

    def create_aggregate(self, context, ifc_class):
        aggregate_collection = bpy.data.collections.new(f"{ifc_class}/Assembly")
        context.scene.collection.children.link(aggregate_collection)
        aggregate = bpy.data.objects.new("Assembly", None)
        aggregate_collection.objects.link(aggregate)
        bpy.ops.bim.assign_class(obj=aggregate.name, ifc_class=ifc_class)
        return aggregate


class BIM_OT_select_parts(bpy.types.Operator):
    """Select Parts"""

    bl_idname = "bim.select_parts"
    bl_label = "Select Parts"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.obj) or context.active_object
        parts = ifcopenshell.util.element.get_parts(tool.Ifc.get_entity(obj))
        parts_objs = set(tool.Ifc.get_object(part) for part in parts)
        selectable_parts_objs = set(context.selectable_objects).intersection(parts_objs)
        for selectable_part_obj in selectable_parts_objs:
            selectable_part_obj.select_set(True)
        return {"FINISHED"}


class BIM_OT_select_aggregate(bpy.types.Operator):
    """Select Aggregate"""

    bl_idname = "bim.select_aggregate"
    bl_label = "Select Aggregate"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.obj) or context.active_object
        aggregate = ifcopenshell.util.element.get_aggregate(tool.Ifc.get_entity(obj))
        aggregate_obj = tool.Ifc.get_object(aggregate)
        if aggregate_obj in context.selectable_objects:
            aggregate_obj.select_set(True)
        return {"FINISHED"}


class BIM_OT_add_part_to_object(bpy.types.Operator, Operator):
    bl_idname = "bim.add_part_to_object"
    bl_label = "Add Part to Object"
    bl_options = {"REGISTER", "UNDO"}
    part_class: bpy.props.StringProperty(name="Class", options={"HIDDEN"})
    part_name: bpy.props.StringProperty(name="Name")
    obj: bpy.props.StringProperty(options={"HIDDEN"})

    def invoke(self, context, event):
        self.part_name = "My " + self.part_class.lstrip("Ifc")
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) or context.active_object
        core.add_part_to_object(
            tool.Ifc,
            tool.Aggregate,
            tool.Collector,
            tool.Blender,
            obj=obj,
            part_class=self.part_class,
            part_name=self.part_name,
        )

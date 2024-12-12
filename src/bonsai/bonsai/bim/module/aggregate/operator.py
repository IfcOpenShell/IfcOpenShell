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
import ifcopenshell.util.element
import bonsai.tool as tool
import bonsai.core.aggregate as core
import bonsai.core.spatial
from bonsai.bim.ifc import IfcStore


class BIM_OT_aggregate_assign_object(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.aggregate_assign_object"
    bl_label = "Assign Object To Aggregation"
    bl_description = (
        "Assign object as an aggregate to the selected IFC elements.\n\n"
        "If called from Bonsai UI, then either 'Relating Whole' or 'Related Part' must be provided.\n"
        "If called directly, active object will be considered a relating whole"
    )
    bl_options = {"REGISTER", "UNDO"}
    relating_object: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

    def _execute(self, context):
        relating_obj = None
        if self.relating_object:
            relating_obj = tool.Ifc.get_object(tool.Ifc.get().by_id(self.relating_object))
        elif self.related_object:
            aggregate = ifcopenshell.util.element.get_aggregate(tool.Ifc.get().by_id(self.related_object))
            if aggregate:
                relating_obj = tool.Ifc.get_object(aggregate)
        elif context.active_object:
            relating_obj = context.active_object
        if not relating_obj:
            self.report({"ERROR"}, "No relating object is provided.")
            return

        assert isinstance(relating_obj, bpy.types.Object)
        for obj in tool.Blender.get_selected_objects():
            if obj == relating_obj:
                continue
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            try:
                core.assign_object(
                    tool.Ifc,
                    tool.Aggregate,
                    tool.Collector,
                    relating_obj=relating_obj,
                    related_obj=obj,
                )
                tool.Aggregate.constrain_parts_to_aggregate(relating_obj)
                props = context.scene.BIMAggregateProperties
                if relating_obj == props.editing_aggregate and props.in_aggregate_mode:
                    new_editing_obj = props.editing_objects.add()
                    new_editing_obj.obj = obj
            except core.IncompatibleAggregateError:
                self.report({"ERROR"}, f"Cannot aggregate {obj.name} to {relating_obj.name}")
            except core.AggregateRepresentationError:
                self.report({"ERROR"}, f"Cannot aggregate to {relating_obj.name} with a body representation")


class BIM_OT_aggregate_unassign_object(bpy.types.Operator, tool.Ifc.Operator):
    """Remove aggregation relationship for selected IFC elements"""

    bl_idname = "bim.aggregate_unassign_object"
    bl_label = "Unassign Object From Aggregation"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        for obj in tool.Blender.get_selected_objects():
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

            tool.Aggregate.apply_constraints(tool.Ifc.get_object(element))

            # Removes Pset related to Linked Aggregates
            if not element.is_a("IfcElementAssembly"):
                pset = ifcopenshell.util.element.get_pset(element, "BBIM_Linked_Aggregate")
                if pset:
                    pset = tool.Ifc.get().by_id(pset["id"])
                    ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=pset)


class BIM_OT_enable_editing_aggregate(bpy.types.Operator):
    """Enable editing aggregation relationship"""

    bl_idname = "bim.enable_editing_aggregate"
    bl_label = "Enable Editing Aggregate"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.enable_editing_aggregate(tool.Aggregate, obj=context.active_object)
        return {"FINISHED"}


class BIM_OT_disable_editing_aggregate(bpy.types.Operator):
    """Disable editing aggregation relationship"""

    bl_idname = "bim.disable_editing_aggregate"
    bl_label = "Disable Editing Aggregate"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_aggregate(tool.Aggregate, obj=context.active_object)
        return {"FINISHED"}


class BIM_OT_add_aggregate(bpy.types.Operator, tool.Ifc.Operator):
    """Add aggregate to IFC element"""

    bl_idname = "bim.add_aggregate"
    bl_label = "Add Aggregate"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    ifc_class: bpy.props.StringProperty(name="IFC Class", default="IfcElementAssembly")
    aggregate_name: bpy.props.StringProperty(name="Name", default="Default_Name")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.prop(self, "ifc_class")
        row = self.layout
        row.prop(self, "aggregate_name")

    def _execute(self, context):
        try:
            ifc_class = tool.Ifc.schema().declaration_by_name(self.ifc_class).name()
        except:
            return
        aggregate = self.create_aggregate(context, ifc_class, self.aggregate_name)

        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue

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
                bonsai.core.spatial.assign_container(
                    tool.Ifc,
                    tool.Collector,
                    tool.Spatial,
                    container=current_container,
                    element_obj=aggregate,
                )
            core.assign_object(tool.Ifc, tool.Aggregate, tool.Collector, relating_obj=aggregate, related_obj=obj)
            tool.Aggregate.constrain_parts_to_aggregate(aggregate)

    def create_aggregate(self, context, ifc_class, aggregate_name):
        aggregate = bpy.data.objects.new(aggregate_name, None)
        aggregate.location = context.scene.cursor.location
        bpy.ops.bim.assign_class(obj=aggregate.name, ifc_class=ifc_class)
        return aggregate


class BIM_OT_select_parts(bpy.types.Operator):
    """Select Parts"""

    bl_idname = "bim.select_parts"
    bl_label = "Select Parts"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        for obj in context.selected_objects:
            parts = ifcopenshell.util.element.get_parts(tool.Ifc.get_entity(obj))
            if parts:
                parts_objs = set(tool.Ifc.get_object(part) for part in parts)
                selectable_parts_objs = set(context.selectable_objects).intersection(parts_objs)
                for selectable_part_obj in selectable_parts_objs:
                    selectable_part_obj.select_set(True)
            else:
                obj.select_set(False)
        return {"FINISHED"}


class BIM_OT_select_aggregate(bpy.types.Operator):
    """Select Aggregate"""

    bl_idname = "bim.select_aggregate"
    bl_label = "Select Aggregate"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    select_parts: bpy.props.BoolProperty(default=False)

    @classmethod
    def description(cls, context, properties):
        if properties.select_parts:
            return "Select Aggregate and Parts"
        else:
            return "Select Aggregate"

    def execute(self, context):
        all_parts = []
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                aggregate = ifcopenshell.util.element.get_aggregate(element)
                if aggregate:
                    all_parts.append(aggregate)
                    obj.select_set(False)
                else:
                    pass
            if not element:
                obj.select_set(False)

        if self.select_parts:
            all_objs = []
            for part in all_parts:
                if part.IsDecomposedBy:
                    for subpart in part.IsDecomposedBy[0].RelatedObjects:
                        all_parts.append(subpart)
                all_objs.append(part)

            for element in all_objs:
                obj = tool.Ifc.get_object(element)
                if obj:
                    obj.select_set(True)

        else:
            for aggregate_element in all_parts:
                aggregate_obj = tool.Ifc.get_object(aggregate_element)
                aggregate_obj.select_set(True)
                bpy.context.view_layer.objects.active = aggregate_obj

        return {"FINISHED"}


class BIM_OT_add_part_to_object(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_part_to_object"
    bl_label = "Add Part to Object"
    bl_options = {"REGISTER", "UNDO"}
    part_class: bpy.props.StringProperty(name="Class", options={"HIDDEN"})
    part_name: bpy.props.StringProperty(name="Name")
    element: bpy.props.IntProperty(options={"HIDDEN"})

    def invoke(self, context, event):
        self.part_name = "My " + self.part_class.lstrip("Ifc")
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        core.add_part_to_object(
            tool.Ifc,
            tool.Aggregate,
            tool.Collector,
            tool.Blender,
            obj=tool.Ifc.get_object(tool.Ifc.get().by_id(self.element)) if self.element else context.active_object,
            part_class=self.part_class,
            part_name=self.part_name,
        )
        bonsai.core.spatial.import_spatial_decomposition(tool.Spatial)


class BIM_OT_break_link_to_other_aggregates(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.break_link_to_other_aggregates"
    bl_label = "Break link to other aggregates"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        aggregate = ifcopenshell.util.element.get_aggregate(element)
        if not aggregate:
            return []
        if not element:
            return []

        parts = ifcopenshell.util.element.get_parts(aggregate)

        for part in parts:
            pset = ifcopenshell.util.element.get_pset(part, "BBIM_Linked_Aggregate")
            pset = tool.Ifc.get().by_id(pset["id"])
            ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=part, pset=pset)

        linked_aggregate_group = next(
            r.RelatingGroup
            for r in getattr(aggregate, "HasAssignments", [])
            if r.is_a("IfcRelAssignsToGroup")
            if "BBIM_Linked_Aggregate" in r.RelatingGroup.Name
        )
        tool.Ifc.run("group.unassign_group", group=linked_aggregate_group, products=[aggregate])

        return {"FINISHED"}


class BIM_OT_select_linked_aggregates(bpy.types.Operator):
    bl_idname = "bim.select_linked_aggregates"
    bl_label = "Select linked aggregates"
    bl_options = {"REGISTER", "UNDO"}
    select_parts: bpy.props.BoolProperty(default=False)

    @classmethod
    def description(cls, context, properties):
        if properties.select_parts:
            return "Select all aggregates, subaggregates and all their parts"
        else:
            return "Select all aggregates"

    def execute(self, context):
        for obj in context.selected_objects:
            obj.select_set(False)
            element = tool.Ifc.get_entity(obj)
            aggregate = ifcopenshell.util.element.get_aggregate(element)
            if not aggregate:
                continue
            if not element:
                continue

            linked_aggregate_group = next(
                r.RelatingGroup
                for r in getattr(aggregate, "HasAssignments", [])
                if r.is_a("IfcRelAssignsToGroup")
                if "BBIM_Linked_Aggregate" in r.RelatingGroup.Name
            )

            group_rel = linked_aggregate_group.IsGroupedBy
            for group_link in group_rel:
                parts = list(group_link.RelatedObjects)
                if self.select_parts:
                    parts_objs = []
                    for part in parts:
                        if part.IsDecomposedBy:
                            for subpart in part.IsDecomposedBy[0].RelatedObjects:
                                parts.append(subpart)
                        parts_objs.append(part)

                    for element in parts_objs:
                        obj = tool.Ifc.get_object(element)
                        if obj:
                            obj.select_set(True)
                else:
                    for element in parts:
                        obj = tool.Ifc.get_object(element)
                        obj.select_set(True)

        return {"FINISHED"}

class BIM_OT_disable_aggregate_mode(bpy.types.Operator):
    bl_idname = "bim.disable_aggregate_mode"
    bl_label = "Disable Aggregate Mode"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.select_all(action="DESELECT")
        bonsai.core.aggregate.disable_aggregate_mode(tool.Aggregate)
        return {"FINISHED"}

class BIM_OT_toggle_aggregate_mode_local_view(bpy.types.Operator):
    bl_idname = "bim.toggle_aggregate_mode_local_view"
    bl_label = "Toggle Aggregate Mode Local View"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMAggregateProperties
        objs = [o.obj for o in props.editing_objects]
        if props.in_aggregate_mode:
            if context.space_data.local_view:
                bpy.ops.view3d.localview()
            else:
                for obj in objs:
                    obj.select_set(True)
                bpy.ops.view3d.localview()

        return {"FINISHED"}

class BIM_OT_aggregate_assing_new_objects_in_aggregate_mode(bpy.types.Operator):
    bl_idname = "bim.aggregate_assing_new_objects_in_aggregate_mode"
    bl_label = "Aggregate Assing New Objects In Aggregate Mode"
    bl_options = {"REGISTER", "UNDO"}
    relating_object: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

    def execute(self, context):
        bpy.ops.object.select_all(action="DESELECT")
        props = context.scene.BIMAggregateProperties
        editing_objects = set([o.obj for o in props.editing_objects])
        not_editing_objects = set([o.obj for o in props.not_editing_objects])
        objs = []
        visible_objects = tool.Raycast.get_visible_objects(context)
        for obj in visible_objects:
            if obj.visible_in_viewport_get(context.space_data):
                objs.append(obj.original)
        new_objs = set(objs) - not_editing_objects - editing_objects
        new_objs = [o for o in new_objs if o.data]
        for obj in new_objs:
            element = tool.Ifc.get_entity(obj)
            if element and element.is_a("IfcElement"):
                obj.select_set(True)
                editing_obj = props.editing_objects.add()
                editing_obj.obj = obj
                props.editing_aggregate.select_set(True)
        self.relating_object = tool.Ifc.get_entity(props.editing_aggregate).id()
        self.related_object = tool.Ifc.get_entity(obj).id()
        BIM_OT_aggregate_assign_object._execute(self, context)

        return {"FINISHED"}

